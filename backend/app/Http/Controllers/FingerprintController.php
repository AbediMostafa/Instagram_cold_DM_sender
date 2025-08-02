<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Arr;

class FingerprintController extends Controller
{
    public function create()
    {
        $fingerprint = [];
        $fingerprints = config('fingerprints');

        $browser = Arr::random($fingerprints["browsers"]);
        $hardwareConcurrency = Arr::random($fingerprints["hardware_concurrences"]);
        $deviceMemory = Arr::random($fingerprints["device_memories"]);
        $macPrefix = Arr::random($fingerprints["mac_prefixes"]);
        $webglConfig = Arr::random($fingerprints["webgl_configs"]);

        $suffix = collect(range(1, 3))
            ->map(fn() => str_pad(dechex(mt_rand(0, 255)), 2, '0', STR_PAD_LEFT))
            ->implode(':');

        $macAddress = strtoupper($macPrefix . ':' . $suffix);
        function generateRandomDeviceName(): string
        {
            $prefix = 'DESKTOP-';
            $characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            $suffix = '';

            for ($i = 0; $i < 7; $i++)
                $suffix .= $characters[random_int(0, strlen($characters) - 1)];

            return $prefix . $suffix;
        }


        $fingerprint['fingerprint_config'] = [
            'ua' => $browser['ua'],
            'webgl_config' => $webglConfig,
            'hardware_concurrency' => $hardwareConcurrency,
            'device_name' => generateRandomDeviceName(),
            'mac_address_config' => [
                "model" => "2",
                "address" => $macAddress
            ],
            'browser_kernel_config'=>$browser['browser_kernel_config'],
            'device_memory'=>$deviceMemory
        ];

        return $fingerprint;
    }
}
