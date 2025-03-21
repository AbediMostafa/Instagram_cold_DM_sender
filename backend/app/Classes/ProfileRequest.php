<?php

namespace App\Classes;

use App\Models\Setting;
use Dotenv\Dotenv;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ProfileRequest
{
    protected $baseUrl;
    protected $email;
    protected $password;

    public function __construct()
    {

        Dotenv::createImmutable(__DIR__ . "/../..")->load();

        $this->baseUrl = "https://api.multilogin.com/user/signin";
//        $this->baseUrl = env('MLX_BASE');
        $this->email = env('MLX_USERNAME');
        $this->password = env('MLX_PASSWORD');
    }

    public function request(string $type, string $url, array $data = null)
    {
        $getHeaders = fn() => [
            "Accept" => "application/json",
            "Content-Type" => "application/json",
            "Authorization" => "Bearer " . Setting::getValue('mlx_token'),
        ];

        $sendRequest = fn() => $type === 'get'
            ? Http::withoutVerifying()->withHeaders($getHeaders())->get($url)
            : Http::withoutVerifying()->withHeaders($getHeaders())->post($url, $data);

        $response = $sendRequest();

        if ($response->unauthorized()) {
            $this->renewToken();
            return $sendRequest();
        }

        if ($response->failed()) {
            throw new \Exception("Error while sending MLX {$type} request: " . $response->body());
        }

        return $response;
    }

    /**
     * @throws ConnectionException
     */
    public function renewToken(): void
    {

        if (Setting::getValue('mlx_lock') === 'True') return;

        Setting::setValue('mlx_lock', 'True');

        try {
            $hashedPassword = md5($this->password);

            $payload = [
                'email' => $this->email,
                'password' => $hashedPassword,
            ];

            $response = Http::withoutVerifying()->post($this->baseUrl, $payload);

            if ($response->failed()) {
                throw new \Exception("Error during login: " . $response->body());
            }


            $token = $response->json('data.token');

            Setting::setValue('mlx_token', $token);
        } catch (\Exception $e) {
            Log::error("MLX Token Renewal Failed: " . $e->getMessage());
            throw $e;
        } finally {
            Setting::setValue('mlx_lock', 'False');
        }
    }
}
