<?php

namespace App\Models;

use App\Classes\AdsPowerProfileUpdateProxy;
use App\Classes\MultiloginService;
use App\Classes\ProfileDelete;
use App\Classes\ProfileUpdateProxy;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class Account extends Model
{
    use HasFactory;

    protected $guarded = [];

    public static array $instagramStates = [
        'active',
        'challenging',
        'follow ban',
        'login required',
        'action ban',
        'bad password',
        'proxy blocked',
        'wait a few minutes',
        'two factor required',
        'doesnt followed dm limit',
        'suspended',
    ];

    public static array $appStates = [
        'idle',
        'processing',
        'set name',
        'set username',
        'set bio',
        'set avatar',
        'post image',
        'post carousel',
        'post video',
        'following',
        'sending DM',
        'make public',
        'loom follow up',
        'delete initial posts',
        'get thread messages'
    ];

    public function threads()
    {
        return $this->hasMany(Thread::class);
    }

    public function leads()
    {
        return $this->hasMany(Lead::class);
    }

    public function clis()
    {
        return $this->hasMany(Cli::class);
    }

    public function templates()
    {
        return $this->belongsToMany(Template::class);
    }

    public function proxy()
    {
        return $this->belongsTo(Proxy::class);
    }

    public function category(): \Illuminate\Database\Eloquent\Relations\BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function color()
    {
        return $this->belongsTo(Color::class);
    }

    public function notifs()
    {
        return $this->hasMany(Notif::class);
    }

    public function commands()
    {
        return $this->hasMany(Command::class);
    }

    public function looms()
    {
        return $this->hasMany(Loom::class);
    }

    public function service()
    {
        return $this->belongsTo(Service::class);
    }

    public function specs()
    {
        return $this->hasOne(AccountSpec::class);
    }

    public function automationQueues()
    {
        return $this->hasMany(AutomationQueue::class);
    }

    public static function createOne()
    {
        $secretKey = str_replace(' ', '', r('secret_key'));

        $account = Account::query()->create([
            'username' => r('username'),
            'password' => r('password'),
            'secret_key' => $secretKey,
            'service_id' => r('service_id'),
        ]);

        !empty(r('tags')) && $account->tags()->attach(r('tags'));

        return $account;
    }

    public static function createBulk()
    {
        $lines = explode("\n", request('accounts'));
        $existsAccounts = '';
        $accounts = [];

        foreach ($lines as $line) {
            $account = explode(',', $line);

            $accountExists = Account::query()
                ->whereUsername($account[0])
//                ->wherePassword($account[1])
                ->exists();

            if ($accountExists) {
                $existsAccounts .= $account[0] . ':' . $account[0] . "\n";
                continue;
            }

            $accountObj = Account::query()->create([
                'username' => $account[0],
                'password' => $account[1],
                'secret_key' => array_key_exists(2, $account) ? str_replace(' ', '', $account[2]) : null,
                'email' => array_key_exists(3, $account) ? $account[3] : null,
                'email_password' => array_key_exists(4, $account) ? $account[4] : null,
                'username_changed' => r('username_changed'),
                'created_at' => Carbon::now(),
                'category_id' => r('category'),
                'service_id' => r('service_id'),
            ]);

            !empty(r('tags')) && $accountObj->tags()->attach(r('tags'));

            r('start_profile') && runPythonProcess('new.py', $accountObj->id);
        }

        abort_if($existsAccounts, 403, 'These accounts already exists :' . "\n" . $existsAccounts);
        return true;
    }

    public function warnings()
    {
        return $this->hasMany(Warning::class);
    }

    public function tags()
    {
        return $this->morphToMany(Tag::class, 'taggable');
    }

    public function profile()
    {
        return $this->belongsTo(Profile::class);
    }


    public function updateProfileProxyToCustom()
    {
        if ($this->profile) {
            sleep(3);

            if (Profile::is_('adspower')) {

                return (new AdsPowerProfileUpdateProxy($this->profile->profile_id))->updateProxyToCustom($this->profile);
            }

            try {
                $updateProxy = new ProfileUpdateProxy($this->profile->profile_id);
                $updateProxy->getProfile()->updateProxyToCustom();
            } catch (\Exception $exception) {
                dump($exception->getMessage());
                dump($this->username);
            }
        } else {
            dump("{$this->username} dont have profile");
        }
    }

    public function dumpProxy(): void
    {
        if ($this->profile) {
            try {
                $updateProxy = new ProfileUpdateProxy($this->profile->profile_id);
                $updateProxy->getProfile()->dumpProxy();
                sleep(4);
            } catch (\Exception $exception) {
                dump($this->username);
                dd($exception->getMessage());

            }
        }
    }

    public function getProxy()
    {
        if ($this->profile) {
            try {
                $updateProxy = new ProfileUpdateProxy($this->profile->profile_id);
                return $updateProxy->getProfile()->getProxy();
            } catch (\Exception $exception) {
                return $exception->getMessage() . $exception->getTraceAsString();
            }
        }
        return 'Account dont have profile';
    }


    public function makeActive()
    {
        $this->warnings()->delete();
        $this->instagram_state = 'active';
        $this->next_login = null;
        $this->save();
    }

    /**
     * Scope: free & active accounts
     */
    public function scopeFree($query)
    {
        return $query->where('is_used', 0)
            ->where('instagram_state', 'active');
    }

    public static function getNext($limit)
    {
        $query = Account::query()->free();

        if ($query->doesntExist()) {
            Account::query()->update(['is_used' => 0]);
        }

        $accounts = Account::query()
            ->orderBy('id')
            ->limit($limit)
            ->free()
            ->get();

        Account::query()->whereIn('id', $accounts->pluck('id'))->update(['is_used' => 1]);

        return $accounts;
    }

    public function updateProfile($profile, $proxy)
    {
        $payload = [];

        $storageState = $this->getStorageState();

        if (
            empty($storageState) ||
            !isset($storageState['cookies']) ||
            !is_array($storageState['cookies'])
        ) {
            $this->addCli("Account storage state invalid");
            $storageState = "";
        }

//        $payload['profile_id'] = 'sldfj';
        $payload['profile_id'] = $profile->profile_id;

        if ($storageState) {
            $payload['cookie'] = json_encode($storageState['cookies']);
        }

        $payload["user_proxy_config"] = [
            "proxy_soft" => "other",
            "proxy_type" => "socks5",
            "proxy_host" => $proxy->ip,
            "proxy_port" => $proxy->port,
            "proxy_user" => $proxy->username,
            "proxy_password" => $proxy->password,
        ];

        $url = "http://local.adspower.net:50325/api/v2/browser-profile/update";

        $maxRetries = 5;
        $retryDelay = 2;

        for ($attempt = 1; $attempt <= $maxRetries; $attempt++) {

            $response = Http::withoutVerifying()->post($url, $payload);

            $json = $response->json();

            if ($json['code'] == -1) {
                $this->addCli("Error in profile update : {$json['msg']}");
                throw new \Exception("Error in profile update : {$json['msg']}");
            }

            $this->addCli("Account profile update response (Attempt {$attempt})");
            $this->addCli($json, asJson: true);

            $code = $json['code'] ?? null;
            $msg = $json['msg'] ?? '';

            if (
                $code === -1 &&
                str_contains($msg, 'Too many request')
            ) {
                if ($attempt < $maxRetries) {
                    sleep($retryDelay);
                    continue;
                }

                throw new \Exception(
                    'Maximum retry attempts reached: Too many requests per second'
                );
            }

            break;
        }

        return $json;
    }

    function getStorageState(): array
    {
        $storageState = $this->web_session; // JSON string from DB

        try {
            $decoded = json_decode($storageState, true);

            // Handle double-encoded JSON
            if (is_string($decoded)) {
                $decoded = json_decode($decoded, true);
            }

            return is_array($decoded) ? $decoded : [];
        } catch (\Throwable $e) {
            return [];
        }
    }

    public function addCli($log, bool $asJson = false)
    {
        if ($asJson) {
            $log = json_encode(
                $log,
                JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
            );
        }

        $log = "[{$this->username} -- {$this->id}] \${$log}";

        $truncatedLog = $log ? substr($log, 0, 254) : '';


        return $this->clis()->create(['log' => $truncatedLog]);
    }
}
