<?php

namespace App\Models;

use App\Casts\MessageDateCast;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Message extends Model
{
    use HasFactory;

    protected $guarded = [];

    public $timestamps = false;

    public static array $senders = [
        'account',
        'lead',
    ];

    public static array $types = [
        'text',
        'post',
        'loom',
    ];

    public static array $states = [
        'seen',
        'unseen',
        'pending',
    ];

    protected $casts = [
        'created_at' => MessageDateCast::class,
    ];

    public function changeState($state)
    {
        $this->state = $state;
        $this->save();
    }

    public function getCreatedAtFormattedAttribute()
    {
        return $this->created_at->diffForHumans();
    }

    public function thread()
    {
        return $this->belongsTo(Thread::class);
    }

    public function command()
    {
        return $this->morphOne(Command::class, 'commandable');
    }

    public function messageable()
    {
        return $this->morphTo();
    }
}
