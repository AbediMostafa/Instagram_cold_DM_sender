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

        $url = "http://127.0.0.1:50325/api/v1/user/delete";
        $response = Http::withoutVerifying()->post($url, $payload,  proxies={
            'http': None,
            'https': None,
        });

        if ($response->failed()) {
            throw new \Exception("Error while Deleting profile " . $response->body());
        }

        return $this;
    }
}
