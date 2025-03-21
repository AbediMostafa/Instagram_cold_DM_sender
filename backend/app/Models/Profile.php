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

    public static function getWithoutAccountProfiles()
    {

        $request = new ProfileRequest();

        $resp = $request->request('get', 'https://launcher.mlx.yt:45001/api/v1/profile/statuses');

        $data = collect($resp->json()["data"]["states"])->keys();

        $resp = $request->request('post', 'https://api.multilogin.com/profile/metas', ['ids' => $data]);
        $profiles = $resp->json()["data"]["profiles"];

        $profiles = collect($profiles)->pluck("name")->each(function ($title) {

            $profileDb = Profile::query()->where("title", $title)->doesntExist();

            $profileDb && dump($title);
        });
    }

    public static function is_($profileType)
    {
        return Setting::getValue('anti_detect_browser') === $profileType;
    }
}
