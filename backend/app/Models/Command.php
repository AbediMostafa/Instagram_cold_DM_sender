<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Command extends Model
{
    use HasFactory;

    protected $guarded = [];

    public static array $states = [
        'pending',
        'processing',
        'success',
        'fail',
    ];

    public static array $types = [
        'set name',
        'set username',
        'set bio',
        'set avatar',
        'post image',
        'post video',
        'post carousel',
        'follow',
        'dm follow up',
        'like post',
        'comment post',
        'custom message',
        'send loom',
        'loom follow up',
        'get threads',
        'delete initial posts',
        'get thread messages',
        'call booked',
        'number of active accounts',
    ];

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function commandable()
    {
        return $this->morphTo();
    }
}
