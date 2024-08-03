<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Notif extends Model
{
    use HasFactory;

    public $timestamps = false;

    public static array $visibility = [
        'seen',
        'unseen',
    ];


    public function account()
    {
        return $this->belongsTo(Account::class);

    }

    public function lead()
    {
        return $this->belongsTo(Lead::class);

    }

    public function thread()
    {
        return $this->belongsTo(Thread::class);
    }

    public function message()
    {
        return $this->belongsTo(Message::class);
    }
}
