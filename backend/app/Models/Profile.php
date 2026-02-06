<?php

namespace App\Models;

use App\Classes\ProfileDelete;
use App\Classes\ProfileDeleteAdsPower;
use App\Classes\ProfileRequest;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Profile extends Model
{
    use HasFactory;

    protected $guarded = [];

    public function accounts()
    {
        return $this->hasMany(Account::class);
    }

    public function proxy()
    {
        return $this->belongsTo(Proxy::class);
    }


    public static function getNext()
    {
        $query = Profile::query()->where('is_used', 0);

        if ($query->doesntExist()) {
            Profile::query()->update(['is_used' => 0]);
        }

        $profile = $query->orderBy('id')->first();
        $profile->is_used = 1;
        $profile->save();

        return $profile;
    }

    public static function getWithFewestAccounts()
    {
        return Profile::query()
            ->withCount('accounts')
            ->orderBy('accounts_count', 'asc')
            ->first();
    }

    public static function averageAccountCount()
    {
        return Profile::query()
            ->withCount('accounts')
            ->get()->avg('accounts_count');
    }

    public function setProxyIdTo($proxyId)
    {
        $this->proxy_id = $proxyId;
        $this->save();
    }

    public function deleteRecords()
    {
        try {
            DB::beginTransaction();
            $this->delete();

            $obj = Profile::is_('adspower') ?
                new ProfileDeleteAdsPower($this->profile_id) : new ProfileDelete($this->profile_id);

            $obj->deleteProfile();

            DB::commit();

        } catch (\Exception $exception) {

            DB::rollBack();
            throw $exception;
        }
    }

    public static function is_($profileType)
    {
        return Setting::getValue('anti_detect_browser') === $profileType;
    }
}
