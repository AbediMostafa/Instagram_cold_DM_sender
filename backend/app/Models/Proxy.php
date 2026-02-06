<?php

namespace App\Models;

use Carbon\Carbon;
use http\Exception\RuntimeException;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use GuzzleHttp\Client;

class Proxy extends Model
{
    use HasFactory;

    protected $guarded = [];
    public $timestamps = false;

    public static array $states = [
        'active',
        'inactive',
    ];

    public function accounts()
    {
        return $this->hasMany(Account::class);
    }

    public function profiles()
    {
        return $this->hasMany(Profile::class);
    }

    public static function createBulk()
    {
        $lines = explode("\n", request('proxies'));
        $existsProxies = '';
        $proxies = [];

        foreach ($lines as $line) {
            $proxy = explode(':', $line);
            if (count($proxy) === 5) {

                $proxyExists = Proxy::query()
                    ->whereIp($proxy[0])
                    ->wherePort($proxy[1])
                    ->exists();

                if ($proxyExists) {
                    $existsProxies .= $proxy[0] . ':' . $proxy[0] . "\n";
                    continue;
                }

                $proxies[] = [
                    'ip' => $proxy[0],
                    'port' => $proxy[1],
                    'username' => $proxy[2],
                    'password' => $proxy[3],
                    'type' => $proxy[4],
                ];
            }
        }

        Proxy::query()->insert($proxies);
        abort_if($existsProxies, 403, 'These proxies already exists :' . "\n" . $existsProxies);
    }

    public static function createOne()
    {
        Proxy::query()->create([
            'ip' => request('ip'),
            'port' => request('port'),
            'username' => request('username'),
            'password' => request('password'),
        ]);
    }

    public static function getWithFewestProfiles()
    {
        return Proxy::query()
            ->withCount('profiles')
            ->orderBy('profiles_count', 'asc')
            ->first();
    }

    public static function getWithFewestAccounts()
    {
        return Proxy::query()
            ->withCount('accounts')
            ->orderBy('accounts_count', 'asc')
            ->first();
    }

    public function fetchExternalIpViaProxy(int $timeout = 10): ?string
    {
        $auth = '';

        if ($this->username && $this->password) {
            $auth =
                rawurlencode($this->username)
                . ':'
                . rawurlencode($this->password)
                . '@';
        }

        $thisUrl = "socks5://{$auth}{$this->ip}:{$this->port}";

        $client = new Client([
            'timeout' => $timeout,
            'proxy' => [
                'http' => $thisUrl,
                'https' => $thisUrl,
            ],
            'headers' => [
                'User-Agent' => 'proxy-ip-checker/1.0',
            ],
            'verify' => false, // avoid SSL issues via proxy
        ]);

        $endpoints = [
            'https://httpbin.org/ip',
            'https://ifconfig.co/ip',
            'https://api.ipify.org?format=json',
        ];

        foreach ($endpoints as $url) {
            try {
                $response = $client->get($url);
                $body = trim((string)$response->getBody());
                $contentType = $response->getHeaderLine('Content-Type');

                // JSON response
                if (str_contains($contentType, 'json')) {
                    $json = json_decode($body, true);
                    if (is_array($json) && isset($json['ip'])) {
                        return trim($json['ip']);
                    }
                }

                // Plain text / regex fallback
                if (preg_match('/(\d{1,3}(?:\.\d{1,3}){3})/', $body, $m)) {
                    return $m[1];
                }
            } catch (RequestException $e) {
                continue;
            } catch (\Throwable $e) {
                continue;
            }
        }

        return null;
    }

    public static function getNext($proxyType)
    {
        $query = Proxy::query()
            ->where('is_used', 0)
            ->where('type', $proxyType);

        if ($query->doesntExist()) {

            Proxy::query()
                ->where('type', $proxyType)
                ->update(['is_used' => 0]);
        }

        /** @var Proxy|null $proxy */
        $proxy = $query->orderBy('id')->first();

        if (!$proxy) {
            return null;
        }

        $proxy->is_used = 1;
        $proxy->save();

        return $proxy;
    }

    public static function getFreeProxy(
        Account $account,
        int     $maxCheckTimeout = 10,
        int     $stuckThresholdMinutes = 5,
        int     $maxAttempts = 50
    ): Proxy
    {
        $proxyType = Setting::getValue('proxy_type');
        $attempts = 0;

        $account->addCli("Proxy type : $proxyType");

        while ($attempts < $maxAttempts) {
            $attempts++;
            $proxy = self::getNext($proxyType);

            $account->addCli("Selected proxy : {$proxy->ip} : {$proxy->port}");
            $account->addCli("Previous real IP : {$proxy->real_ip}");

            $observedIp = $proxy->fetchExternalIpViaProxy($maxCheckTimeout);
            $account->addCli("Observed IP : $observedIp");

            if (!$observedIp) {
                $account->addCli("Observed IP is None trying next one ");
                continue;
            }

            $now = now('Asia/Tehran');

            if (!$proxy->real_ip_checked_at) {
                $proxy->real_ip = $observedIp;
                $proxy->real_ip_checked_at = $now;
                $proxy->save();

                return $proxy;
            }

            $prevChecked = Carbon::parse($proxy->real_ip_checked_at);

            if ($proxy->real_ip === $observedIp) {
                $minutes = $prevChecked->diffInMinutes($now);
                $account->addCli("Real IP is same as observed IP");


                if ($minutes <= $stuckThresholdMinutes) {
                    $account->addCli("But $stuckThresholdMinutes not passed");
                    return $proxy;
                }

                $account->addCli("Proxy stuck for $minutes minutes trying next one ");

                continue;
            }

            $account->addCli("Real IP is different than observed IP");
            $proxy->real_ip = $observedIp;
            $proxy->real_ip_checked_at = $now;
            $proxy->save();

            return $proxy;
        }

        throw new RuntimeException('No valid rotating proxy found after max attempts');
    }
}
