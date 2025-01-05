<?php

namespace App\Classes;


use App\Models\Account;
use App\Models\Profile;
use App\Models\Proxy;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;
use Dotenv\Dotenv;


class ProfileMakerV2
{
    public $account;
    public $proxy;
    public $responseMessage='';
    public static $instance;
    public ProfileRequest $request;


    public $payload = [
        "name" => "",
        "browser_type" => "mimic",
        "folder_id" => "",
        "os_type" => "windows",
        "parameters" => [
            "flags" => [
                "navigator_masking" => "mask",
                "audio_masking" => "natural",
                "localization_masking" => "mask",
                "geolocation_popup" => "prompt",
                "geolocation_masking" => "mask",
                "timezone_masking" => "mask",
                "graphics_noise" => "mask",
                "graphics_masking" => "mask",
                "webrtc_masking" => "mask",
                "fonts_masking" => "mask",
                "media_devices_masking" => "natural",
                "screen_masking" => "mask",
                "canvas_noise" => "natural",
                "startup_behavior" => "recover",
                "ports_masking" => "mask",
                "proxy_masking" => "custom",

            ],
            "storage" => [
                "is_local" => true,
                "save_service_worker" => true
            ],
            "proxy" => [
                "type" => "http",
                "host" => "",
                "port" => "",
                "username" => "",
                "password" => ""
            ],
            "custom_start_urls" => ["https://www.instagram.com/"],
            "fingerprint" => [
                "localization" => null,
                "timezone" => null,
                "webrtc" => null,
                "geolocation" => null
            ],
        ]
    ];


    public function __construct(public $accountIds = [])
    {
        $this->folderId = env('MLX_FOLDER_ID', "b64c9aa8-7863-40d7-8398-1d52ef8cfe41");
        $this->folderName = env('MLX_FOLDER_NAME', "mass_dm");

        $dotenv = Dotenv::createImmutable(base_path());
        $dotenv->load();

        $this->request = new ProfileRequest();
    }

    public static function getInstance($accountIds = [],): ProfileMakerV2
    {
        self::$instance = new self($accountIds);

        return self::$instance;
    }

    public function getAccounts()
    {

        $all = Account::whereInstagramState('active')->get();
        $selected = Account::whereInstagramState('active')->whereIn("id", $this->accountIds)->get();

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

            if ($this->account->proxy){
                return 'Account has proxy already';
            }

            return $this->account
                ->proxy()
                ->associate(Proxy::getWithFewestAccounts());
        }

        $this->createProfile();
    }

    public function generateProfileName()
    {
        $uid = $this->account ? $this->account->id : Str::uuid();
        $this->profileName = "profile_$uid";
        return $this;
    }

    public function getProxy()
    {
        $this->proxyObj = Proxy::getWithFewestProfiles();

        $this->proxy = [
            "type" => "http",
            "host" => $this->proxyObj->ip,
            "port" => $this->proxyObj->port,
            "username" => $this->proxyObj->username,
            "password" => $this->proxyObj->password
        ];

        return $this;
    }

    public function getResidentialProxy()
    {
        $residentialProxy = ProfileGetProxy::getResidentialProxy();

        $this->proxy = [
            "type" => "socks5",
            "host" => $residentialProxy->host,
            "port" => (int)$residentialProxy->port,
            "username" => $residentialProxy->username,
            "password" => $residentialProxy->password
        ];

        return $this;
    }

    public function sendRequest()
    {
        $url = env('MLX_CREATE_PROFILE_URL', "https://api.multilogin.com/profile/create");

        $this->response = $this->request->request('post', $url, $this->payload);

        $jsonResponse = $this->response->json();

        $this->responseMessage = $jsonResponse["status"]["message"];
        $this->responseData = $jsonResponse["data"]['ids'][0];

        return $this;
    }

    public function handleRequestErrors()
    {
        $statusCode = $this->response->status();

        abort_if(
            $statusCode != 201,
            403,
            "Error : $statusCode _ $this->responseMessage"
        );

        return $this;
    }

    public function createProfileRecord()
    {
        $this->profile = $this->proxyObj
            ->profiles()
            ->create([
                'title' => $this->profileName,
                'folder' => $this->folderName,
                'profile_id' => $this->responseData,
            ]);

        return $this;
    }

    public function createProfile()
    {

        try {
            $this->generateProfileName();
            $this->payload['name'] = $this->profileName;
            $this->payload['folder_id'] = $this->folderId;

//            $this->getResidentialProxy();
            $this->getProxy();

            $this->payload['parameters']['proxy'] = $this->proxy;

            $this->sendRequest()
                ->handleRequestErrors()
                ->createProfileRecord()
                ->updateAccount();

        } catch (\Exception $exception) {
            abort(403, $exception->getMessage() . $this->responseMessage);
        }

        sleep(5);
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
        return Profile::query()->count() == env('MLX_MAX_ALLOWED_PROFILE');
    }
}
