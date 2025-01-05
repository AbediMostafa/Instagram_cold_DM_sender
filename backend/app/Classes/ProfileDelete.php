<?php

namespace App\Classes;

class ProfileDelete
{
    public ProfileRequest $request;

    public function __construct(public $profileId)
    {
        $this->request = new ProfileRequest();
    }

    public function deleteProfile(): static
    {
        $data = [
            'ids' => [$this->profileId],
            "permanently" => true
        ];

        $response =$this->request->request('post', 'https://api.multilogin.com/profile/remove', $data);

        $result = $response->json();
        dump($result);

        return $this;
    }
}
