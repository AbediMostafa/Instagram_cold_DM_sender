<?php

namespace App\Classes;


class ProxyContainer
{
    public function __construct(public $host, public $port, public $username, public $password, public $id = null)
    {
    }
}
