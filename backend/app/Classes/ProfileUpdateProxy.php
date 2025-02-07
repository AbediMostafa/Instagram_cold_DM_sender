<?php

namespace App\Classes;

use App\Models\Account;
use App\Models\Profile;
use \Illuminate\Support\Facades\Http;

class ProfileUpdateProxy
{
    public array $profile;
    public ProfileRequest $request;


    public function __construct(public $profileId)
    {
        $this->request = new ProfileRequest();
    }

    public function getProfile(): static
    {
        $data = [
            'ids' => [$this->profileId]
        ];

        $response = $this->request->request('post', 'https://api.multilogin.com/profile/metas', $data);

        $this->profile = $response->json('data.profiles')[0];

        return $this;
    }

    public function dumpProxy()
    {
        dump($this->profile["parameters"]["proxy"]);

        if ($this->profile["parameters"]["proxy"]['host'] == "gate.multilogin.com") {
            $account = Account::query()->whereHas('profile',
                function ($profile) {
                    $profile->where('profile_id', $this->profileId);

                }
            )->first()->username;

            dump($account);
        }

    }

    public function getProxy()
    {
        return $this->profile["parameters"]["proxy"];

    }

    public function updateProxyToResidential()
    {
        $this->profile["parameters"]["proxy"]["type"] = "socks5";

        $proxy = ProfileGetProxy::getResidentialProxy();
        $this->updateProxy($proxy);
//        $this->getProfileModel()->setProxyIdTo(null);

        return $proxy->host;
    }

    public function profileHasResidentialProxy()
    {
        return $this->profile["parameters"]["proxy"]['host'] === 'gate.multilogin.com';
    }

    public function getProfileModel()
    {
        return Profile::where('profile_id', $this->profileId)->first();

    }

    public function updateProxyFromResidentialToCustom()
    {
        if ($this->profileHasResidentialProxy()) {
            $this->profile["parameters"]["proxy"]["type"] = "http";
            $proxy = ProfileGetProxy::getCustomProxy();
            $this->updateProxy($proxy);
            $this->getProfileModel()->setProxyIdTo($proxy->id);
            return $proxy->host;
        }

        return null;
    }

    public function updateProxyToCustom()
    {
        $this->profile["parameters"]["proxy"]["type"] = "http";
        $proxy = ProfileGetProxy::getCustomProxy();
        $this->updateProxy($proxy);
        $this->getProfileModel()->setProxyIdTo($proxy->id);
    }

    public function updateProxy(ProxyContainer $proxy): static
    {
        $this->profile["parameters"]["proxy"]["host"] = $proxy->host;
        $this->profile["parameters"]["proxy"]["password"] = $proxy->password;
        $this->profile["parameters"]["proxy"]["port"] = (int)$proxy->port;
        $this->profile["parameters"]["proxy"]["username"] = $proxy->username;

        $this->profile["parameters"]["fingerprint"] = [
            "localization" => null,
            "timezone" => null,
            "webrtc" => null,
            "geolocation" => null
        ];

        $newProfile = [
            'name' => $this->profile['name'],
            'parameters' => $this->profile['parameters'],
            'profile_id' => $this->profileId,
        ];

        $response = $this->request->request('post', 'https://api.multilogin.com/profile/update', $newProfile);

        dump($response->json());
        return $this;
    }
}
