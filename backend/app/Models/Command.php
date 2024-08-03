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
        'follow',
        'dm follow up',
        'custom message',
        'send loom',
        'loom follow up',
        'relief action ban',
        'get threads',
        'delete initial posts',
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
