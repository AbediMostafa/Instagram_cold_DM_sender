<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

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
        'post video',
        'following',
        'sending DM',
        'loom follow up',
        'delete initial posts',
    ];

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

    public static function createOne()
    {
        $secretKey = str_replace(' ', '', r('secret_key'));

        return Account::query()->create([
            'username' => r('username'),
            'password' => r('password'),
            'secret_key' => $secretKey,
            'category' => request('category'),
        ]);
    }

    public static function createBulk()
    {
        $lines = explode("\n", request('accounts'));
        $existsAccounts = '';
        $accounts = [];

        foreach ($lines as $line) {
            $account = explode(',', $line);
            if (count($account) > 2) {

                $accountExists = Account::query()
                    ->whereUsername($account[0])
                    ->wherePassword($account[1])
                    ->exists();

                if ($accountExists) {
                    $existsAccounts .= $account[0] . ':' . $account[0] . "\n";
                    continue;
                }

                $accounts[] = [
                    'username' => $account[0],
                    'password' => $account[1],
                    'secret_key' => str_replace(' ', '', $account[2]),
                    'created_at' => Carbon::now(),
                    'category' => request('category'),
                ];
            }
        }

        Account::query()->insert($accounts);
        abort_if($existsAccounts, 403, 'These accounts already exists :' . "\n" . $existsAccounts);
        return true;
    }

    public function warnings()
    {
        return $this->hasMany(Warning::class);
    }
}
