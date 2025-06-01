<?php

namespace App\Classes;


use App\Models\Account;
use App\Models\Profile;
use App\Models\Proxy;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;
use Dotenv\Dotenv;


class AdspowerProfileMaker
{
    public $account;
    public $proxy;
    public $responseMessage = '';
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
        $this->folderId = "6014402";
    }

    public static function getInstance($accountIds = [],): AdspowerProfileMaker
    {
        self::$instance = new self($accountIds);

        return self::$instance;
    }

    public function getAccounts()
    {

        $all = Account::query()->get();
//        $all = Account::whereInstagramState('active')->get();
        $selected = Account::query()->whereIn("id", $this->accountIds)->get();
//        $selected = Account::whereInstagramState('active')->whereIn("id", $this->accountIds)->get();

        return $this->accountIds ? $selected : $all;
    }

    public function iterateAndAssignProfile()
    {
        $this->getAccounts()
            ->each(
                fn($account) => $this->setAccount($account)->assignProfile()
            );
    }

    public function setAccount($account)
    {
        $this->account = $account;

        return $this;
    }

    public function assignProfile()
    {
        //If account has profile abort
        if ($this->account->profile) {
            return 'Account has profile already';
        }

        //If we have a profile that doesn't have any accounts
        if ($this->profile = Profile::doesntHave('accounts')->first()) {
            return $this->updateAccount();
        }

        /**
         * Let's start create a profile for the account
         */

        //If we reach max profile number should assign proxy to account
        if ($this->hitTheMaxProfileNumber()) {

            if ($this->account->proxy) {
                return 'Account has proxy already';
            }

            return $this->account
                ->proxy()
                ->associate(Proxy::getWithFewestAccounts());
        }

        $this->createProfile();
    }

    public function getProxy()
    {
        $this->proxyObj = Proxy::getWithFewestProfiles();

        $this->proxy = [
            "proxy_soft" => "other",
            "proxy_type" => "http",
            "proxy_host" => $this->proxyObj->ip,
            "proxy_port" => $this->proxyObj->port,
            "proxy_user" => $this->proxyObj->username,
            "proxy_password" => $this->proxyObj->password,
        ];

        return $this;
    }

    public function generateProfileName()
    {
        $uid = $this->account ? $this->account->id : Str::uuid();
        $this->profileName = "profile_$uid";
        return $this;
    }

    public function sendRequest()
    {
        $url = "http://local.adspower.net:50325/api/v1/user/create";
        $this->response = Http::withoutVerifying()->post($url, $this->payload);

        $jsonResponse = $this->response->json();
        $this->responseMessage = $jsonResponse["msg"];
        $this->responseData = $jsonResponse["data"];

        return $this;
    }

    public function handleRequestErrors()
    {
        $statusCode = $this->response->status();

        abort_if(
            $statusCode != 200,
            403,
            "Error : $statusCode _ $this->responseMessage"
        );

        return $this;
    }

    public function createProfileRecord()
    {

        $this->profile = Profile::query()->create([
            'title' => $this->profileName,
            'folder' => $this->folderId,
            'profile_id' => $this->responseData['id'],
            'proxy_id' => $this->proxyObj ? $this->proxyObj->id : null,
        ]);

        return $this;
    }

    public function createProfile()
    {

        try {
            sleep(3);
            $this->generateProfileName();
            $this->payload['name'] = $this->profileName;
            $this->payload['group_id'] = $this->folderId;

            $this->getProxy();

            $this->payload["user_proxy_config"] = $this->proxy;

            $this->sendRequest()
                ->handleRequestErrors()
                ->createProfileRecord()
                ->updateAccount();

        } catch (\Exception $exception) {
            abort(403, $exception->getMessage() . $this->responseMessage);
        }

    }

    public function createResidentialProfile()
    {
        try {
            $this->generateProfileName();
            $this->payload['name'] = $this->profileName;
            $this->payload['folder_id'] = $this->folderId;

            $this->getResidentialProxy();
            $this->payload['parameters']['proxy'] = $this->proxy;

            $this->sendRequest()->handleRequestErrors();

        } catch (\Exception $exception) {
            abort(403, $exception->getMessage() . $this->responseMessage);
        }

        sleep(5);

    }

    public function updateAccount(): static
    {
        $this->account->profile_id = $this->profile->id;
        $this->account->save();

        return $this;
    }

    public function hitTheMaxProfileNumber()
    {
        return Profile::query()->count() == 605;
    }
}
