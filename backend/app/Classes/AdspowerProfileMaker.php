<?php

namespace App\Classes;

use App\Models\Account;
use App\Models\Profile;
use App\Models\Proxy;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

class AdspowerProfileMaker
{
    public $account;
    public $profile;
    public $proxy;
    public $proxyObj;
    public $response;
    public $responseMessage = '';
    public $responseData = '';
    public static $instance;

    public $payload = [
        "name" => "",
        "group_id" => "",
        "user_proxy_config" => [],
        "fingerprint_config" => [
            "language" => ["en-US", "en"],
            "language_switch" => 0,
            "screen_resolution" => "random",
            "random_ua" => [
                "ua_system_version" => ["Windows 10"]
            ]
        ],
    ];

    public function __construct(public $accountIds = [])
    {
        $this->folderId = "5780347";
    }

    public static function getInstance($accountIds = []): self
    {
        return new self($accountIds);
    }

    public function handle()
    {
        if (empty($this->accountIds)) {
            // No accounts given — create AdsPower-only profiles until limit hit
            while (!$this->hitTheMaxProfileNumber()) {
                $this->createProfile(attachToAccount: false, useProxy: false);
            }
        } else {
            // Assign profiles to accounts
            $this->getAccounts()->each(function ($account) {
                $this->setAccount($account)->assignProfile();
            });
        }
    }

    public function getAccounts()
    {
        return Account::query()->whereIn('id', $this->accountIds)->get();
    }

    public function setAccount($account): self
    {
        $this->account = $account;
        return $this;
    }

    public function assignProfile()
    {
        if ($this->account->profile) {
            return 'Account already has profile';
        }

        if ($this->profile = Profile::doesntHave('accounts')->first()) {
            return $this->updateAccount();
        }

        if ($this->hitTheMaxProfileNumber()) {
            return 'Profile limit reached';
        }

        $this->createProfile(attachToAccount: true, useProxy: true);
    }

    public function getProxy(): self
    {
        $this->proxyObj = Proxy::getWithFewestProfiles();

        $this->proxy = [
            "proxy_soft" => "other",
            "proxy_type" => "socks5",
            "proxy_host" => $this->proxyObj->ip,
            "proxy_port" => $this->proxyObj->port,
            "proxy_user" => $this->proxyObj->username,
            "proxy_password" => $this->proxyObj->password,
        ];

        return $this;
    }

    public function generateProfileName(): self
    {
        $uid = $this->account?->id ?? Str::uuid();
        $this->profileName = "profile_$uid";
        return $this;
    }

    public function sendRequest(): self
    {
        $url = "http://local.adspower.net:50325/api/v1/user/create";
        $this->response = Http::withoutVerifying()->post($url, $this->payload);
        $json = $this->response->json();

        $this->responseMessage = $json['msg'] ?? '';
        $this->responseData = $json['data'] ?? [];

        return $this;
    }

    public function handleRequestErrors(): self
    {
        $statusCode = $this->response->status();

        abort_if(
            $statusCode !== 200,
            403,
            "Error $statusCode: $this->responseMessage"
        );

        return $this;
    }

    public function createProfileRecord(): self
    {
        $this->profile = Profile::create([
            'title' => $this->profileName,
            'folder' => $this->folderId,
            'profile_id' => $this->responseData['id'] ?? null,
            'proxy_id' => $this->proxyObj->id ?? null,
        ]);

        return $this;
    }

    public function createProfile(bool $attachToAccount = false, bool $useProxy = true)
    {
        try {
            sleep(3);
            $this->generateProfileName();

            $this->payload['name'] = $this->profileName;
            $this->payload['group_id'] = $this->folderId;

            if ($useProxy) {
                $this->getProxy();
                $this->payload['user_proxy_config'] = $this->proxy;
            } else {
                $this->proxyObj = null;
                $this->payload['user_proxy_config'] = [
                    "proxy_soft" => "no_proxy"
                ];
            }

            $this->sendRequest()
                ->handleRequestErrors()
                ->createProfileRecord();

            if ($attachToAccount) {
                $this->updateAccount();
            }

        } catch (\Exception $e) {
            abort(403, $e->getMessage() . ' | ' . $this->responseMessage);
        }
    }

    public function updateAccount(): self
    {
        $this->account->profile_id = $this->profile->id;
        $this->account->save();

        return $this;
    }

    public function hitTheMaxProfileNumber(): bool
    {
        return Profile::count() >= 50;
    }
}
