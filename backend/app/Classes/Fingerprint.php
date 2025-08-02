<?php
namespace App\Classes;


use Illuminate\Support\Arr;
use Illuminate\Support\Collection;

class Fingerprint
{
    protected array $fingerprints;

    public function __construct()
    {
        $this->fingerprints = config('fingerprints');
    }

    public function generate(): array
    {
        return [
            'fingerprint_config' => $this->buildFingerprintConfig()
        ];
    }

    protected function buildFingerprintConfig(): array
    {
        $browser = $this->randomFromConfig('browsers');
        $hardwareConcurrency = $this->randomFromConfig('hardware_concurrences');
        $deviceMemory = $this->randomFromConfig('device_memories');
        $macPrefix = $this->randomFromConfig('mac_prefixes');
        $webglConfig = $this->randomFromConfig('webgl_configs');

        return [
            'ua' => $browser['ua'],
            'webgl_config' => $webglConfig,
            'hardware_concurrency' => $hardwareConcurrency,
            'device_name' => $this->generateRandomDeviceName(),
            'mac_address_config' => [
                'model' => '2',
                'address' => $this->generateMacAddress($macPrefix),
            ],
            'browser_kernel_config' => $browser['browser_kernel_config'],
            'device_memory' => $deviceMemory,
        ];
    }

    protected function generateMacAddress(string $prefix): string
    {
        $suffix = collect(range(1, 3))
            ->map(fn () => str_pad(dechex(mt_rand(0, 255)), 2, '0', STR_PAD_LEFT))
            ->implode(':');

        return strtoupper($prefix . ':' . $suffix);
    }

    protected function generateRandomDeviceName(): string
    {
        $prefix = 'DESKTOP-';
        $characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        $suffix = '';

        for ($i = 0; $i < 7; $i++) {
            $suffix .= $characters[random_int(0, strlen($characters) - 1)];
        }

        return $prefix . $suffix;
    }

    protected function randomFromConfig(string $key): mixed
    {
        return Arr::random($this->fingerprints[$key] ?? []);
    }
}
