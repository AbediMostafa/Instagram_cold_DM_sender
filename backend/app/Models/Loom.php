<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Loom extends Model
{
    use HasFactory;

    protected $guarded = [];
    public static array $states = ['uploaded', 'pending', 'sent'];


    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function lead()
    {
        return $this->belongsTo(Lead::class);
    }

    public function message()
    {
        return $this->morphOne(Message::class,  'messageable');
    }
}
