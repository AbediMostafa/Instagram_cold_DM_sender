<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Mobile extends Model
{
    protected $guarded = [];

    public $timestamps = false;

    // DuoPlus physical status codes (from cloudPhone/status). Only STATUS_ON
    // is usable; 2/10/11 are transitional; the rest are dead ends.
    const STATUS_NOT_CONFIGURED = 0;
    const STATUS_ON = 1;
    const STATUS_OFF = 2;
    const STATUS_EXPIRED = 3;
    const STATUS_RENEWAL_NEEDED = 4;
    const STATUS_POWERING_ON = 10;
    const STATUS_CONFIGURING = 11;
    const STATUS_CONFIG_FAILED = 12;

    public static array $appStates = ['idle', 'processing', 'error'];

    public function proxy()
    {
        return $this->belongsTo(Proxy::class);
    }

    public function accounts()
    {
        return $this->hasMany(Account::class);
    }

    /**
     * Workers driving this device. Control (workflow, running/stopped) lives
     * on the process row, exactly as it does for web workers.
     */
    public function processes()
    {
        return $this->hasMany(Process::class);
    }

    public function getNextAccount()
    {
        $getNextAccount = fn() => $this->accounts()
            ->orderBy('id')
            ->where('is_used', 0)
            ->first();


        if (!$nextAccount = $getNextAccount()) {
            $this->accounts()->update(['is_used' => 0]);
            $nextAccount = $getNextAccount();
        }

        $nextAccount->is_used = 1;
        $nextAccount->save();

        return $nextAccount;
    }
}
