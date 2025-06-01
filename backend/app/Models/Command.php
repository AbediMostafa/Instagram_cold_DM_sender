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
        'unfollow',
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
        'make public',
        'number of active accounts',
        'follow good pages',
        'explore hashtag',
        'generate lead by followers',
        'generate lead by page engagement',
        'generate lead by post engagement',
    ];
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s', // Change the format as needed
    ];

    public function account()
    {
        return $this->belongsTo(Account::class);
    }
    public function lead()
    {
        return $this->belongsTo(Lead::class);
    }

    public function commandable()
    {
        return $this->morphTo();
    }

    public function category(): \Illuminate\Database\Eloquent\Relations\BelongsTo
    {
        return $this->belongsTo(Category::class);
    }
}
