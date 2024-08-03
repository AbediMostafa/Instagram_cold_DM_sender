<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

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

    public static function createBulk()
    {
        $lines = explode("\n", request('proxies'));
        $existsProxies = '';
        $proxies = [];

        foreach ($lines as $line) {
            $proxy = explode(':', $line);
            if (count($proxy) === 4) {

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
}
