<?php

namespace App\Classes;

use App\Classes\ProxyContainer;
use App\Models\Proxy;
use Illuminate\Http\Client\ConnectionException;
use \Illuminate\Support\Facades\Http;


class ProfileGetProxy
{
    public array $headers;
    public string $host;
    public string $port;
    public string $username;
    public string $password;
    public ProfileGetProxy $obj;
    public ProxyContainer $proxy;
    public ProfileRequest $request;

    public $statusCode;
    public array $proxyData = [
        'country' => "any",
        "protocol" => "socks5",
        "sessionType" => "sticky"
    ];

    public function __construct()
    {
        $this->request = new ProfileRequest();
    }

    /**
     * @throws ConnectionException
     */
    public static function getResidentialProxy(): ProxyContainer
    {
        $obj = new self();

        $obj->getProxy()->validateProxy();

        return $obj->proxy;
    }

    public static function getCustomProxy(): ProxyContainer
    {
        $proxy = Proxy::getWithFewestProfiles();

        return new ProxyContainer(
            host: $proxy->ip,
            port: $proxy->port,
            username: $proxy->username,
            password: $proxy->password,
            id: $proxy->id
        );
    }

    /**
     * @throws ConnectionException
     */
    public function getProxy(): static
    {

        $resp = $this->request->request(
            'post',
            "https://profile-proxy.multilogin.com/v1/proxy/connection_url",
            $this->proxyData
        );

        $data = $resp->json('data');

        [$this->host, $this->port, $this->username, $this->password] = explode(":", $data);

        $this->proxy = new ProxyContainer($this->host, $this->port, $this->username, $this->password);

        return $this;
    }

    /**
     * @throws ConnectionException
     */
    public function validateProxy()
    {
        $data = [
            "host" => $this->host,
            "port" => (int)$this->port,
            "username" => $this->username,
            "password" => $this->password,
            "type" => "socks5",
        ];

        $resp = $this->request->request(
            'post',
            "https://launcher.mlx.yt:45001/api/v1/proxy/validate",
            $data
        );

        $this->statusCode = $resp->json('status.http_code');
    }
}
