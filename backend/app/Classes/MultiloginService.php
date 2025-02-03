<?php

namespace App\Classes;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Cache;
use App\Classes\ProfileRequest;


class MultiloginService
{
    protected $messages = [];
    protected $base_url = "https://launcher.mlx.yt:45001";
    protected $email;
    protected $password;
    protected $request;

    public function __construct()
    {
        $this->request = new ProfileRequest();
    }

    public function getMessages($asJson = true)
    {
        if ($asJson) {
            return json_encode($this->messages, JSON_PRETTY_PRINT);
        }

        return implode(PHP_EOL, $this->messages); // Combine messages into a readable string
    }

    public function getEndpointUrl($profileId)
    {
        $response = $this->startProfile($profileId);

        $data = $response->json()['data'];
        return "http://127.0.0.1:{$data['port']}";
    }

    public function startProfile($profileId)
    {
        try {
            return $this->request->request('get', "{$this->base_url}/api/v2/profile/f/" . env('MLX_FOLDER_ID') . "/p/{$profileId}/start?automation_type=playwright&headless_mode=false");

        } catch (\Exception $exception) {
            $this->addMessage($exception->getMessage());
        }
    }

    public function addMessage($message)
    {
        $this->messages[] = $message;
    }

    public function closeBrowser($profileId)
    {
        $this->request->request('get', "{$this->base_url}/api/v1/profile/stop/p/{$profileId}");
    }
}
