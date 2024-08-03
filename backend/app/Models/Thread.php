<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Thread extends Model
{
    use HasFactory;

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

}
