<?php

namespace App\Classes;

use Illuminate\Support\Facades\Http;

class ProfileDeleteAdsPower
{

    public function __construct(public $profileId)
    {
    }

    public function deleteProfile(): static
    {
        $payload = [
            'user_ids'=>[$this->profileId]
        ];

        $url = "http://local.adspower.net:50325/api/v1/user/delete";
        $response = Http::withoutVerifying()->post($url, $payload);

        if ($response->failed()) {
            throw new \Exception("Error while Deleting profile " . $response->body());
        }

        return $this;
    }
}
