<?php

namespace App\Classes;

use App\Models\Account;
use App\Models\Profile;
use \Illuminate\Support\Facades\Http;

class AdsPowerProfileUpdateProxy
{
    public array $profile;
    public array $proxy = [];


    public function __construct(public $profileId)
    {
    }


    public function updateProxyToResidential()
    {

//        $payload = [
//            "user_id" => $this->profileId,
//            "user_proxy_config" => [
//                "proxy_soft" => "no_proxy",
//            ],
//        ];
//        13522df7473a250c:RNW78Fm5@res.proxy-seller.com:10000
        $payload = [
            "user_id" => $this->profileId,
            "user_proxy_config" => [
                "proxy_soft" => "other",
                "proxy_type" => "http",
                "proxy_host" => "res.proxy-seller.com",
                "proxy_port" => 10000,
                "proxy_user" => "13522df7473a250c",
                "proxy_password" => "RNW78Fm5@res",
            ],
        ];

        $url = "http://local.adspower.net:50325/api/v1/user/update";

        $res = Http::withoutVerifying()->post($url, $payload);
        return true;
    }

    public function updateProxyToCustom($profile)
    {
        $proxy = $profile->proxy;

        if ($proxy) {

            $payload = [
                "user_id" => $this->profileId,
                "user_proxy_config" => [
                    "proxy_soft" => "other",
                    "proxy_type" => "socks5",
                    "proxy_host" => $proxy->ip,
                    "proxy_port" => $proxy->port,
                    "proxy_user" => $proxy->username,
                    "proxy_password" => $proxy->password,
                ],
            ];

            $url = "http://local.adspower.net:50325/api/v1/user/update";

            $response = Http::withoutVerifying()->post($url, $payload);
        }
    }
}
