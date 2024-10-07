<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Thread extends Model
{
    use HasFactory;
    public $timestamps = false;

    public function messages()
    {
        return $this->hasMany(Message::class);
    }

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function lead()
    {
        return $this->belongsTo(Lead::class);
    }

    public function notifs()
    {
        return $this->hasMany(Notif::class);
    }

    public function category()
    {
        return $this->belongsTo(Category::class);
    }

    public function makeSeenUnseenMessages()
    {
        $this->messages()
            ->where('state', 'unseen')
            ->update(['state' => 'seen']);
    }
}
