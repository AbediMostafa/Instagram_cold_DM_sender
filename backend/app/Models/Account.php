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

    public function updateProfileProxyFromResidentialToCustom()
    {
        if ($this->profile) {
            sleep(5);

            try {
                $updateProxy = new ProfileUpdateProxy($this->profile->profile_id);
                $updateProxy->getProfile();
                return $updateProxy->updateProxyFromResidentialToCustom();

            } catch (\Exception $exception) {
                dump($exception->getMessage() . $exception->getTraceAsString());
            }
        } else {
            return "{$this->username} dont have profile";
        }
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

    /**
     * Scope: filter by specific IDs
     */
    public function scopeWithSpecificIds($query, ?array $ids)
    {
        if ($ids) {
            $query->whereIn('id', $ids);
        }

        return $query;
    }

    /**
     * Scope: filter by tag titles
     */
    public function scopeWithTags($query, ?array $tagTitles)
    {
        if ($tagTitles) {
            $query->whereHas('tags', function ($q) use ($tagTitles) {
                $q->whereIn('title', $tagTitles);
            });
        }

        return $query;
    }

    public static function next_account($serviceId = null, $specificIds = [], $tagTitles = [])
    {
        $query = Account::query();

        if ($serviceId) {
            $query->where('service_id', $serviceId);
        }

        return $query
            ->free()
            ->withSpecificIds($specificIds)
            ->withTags($tagTitles)
            ->orderBy('id')
            ->lock(DB::raw('FOR UPDATE SKIP LOCKED'))
            ->first();
    }

    public static function resetIsUsed($serviceId = null)
    {
        $query = Account::query();

        if ($serviceId) {
            $query->where('service_id', $serviceId);
        }

        $query->update(['is_used' => false]);
    }
}
