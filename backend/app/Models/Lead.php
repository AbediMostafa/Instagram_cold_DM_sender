<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Lead extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s', // Change the format as needed
    ];

    public $timestamps = false;

    public static array $states = [
        'free',
        'followed',

        'dm follow up',
        'unseen dm reply',
        'seen dm reply',

        'needs response',

        'interested',
        'not interested',

        'loom follow up',
        'unseen loom reply',
        'seen loom reply',
    ];

    public function makeSeen()
    {
        if (in_array($this->last_state, ['unseen dm reply', 'unseen loom reply'])) {

            $this->last_state = match ($this->last_state) {
                'unseen dm reply' => 'seen dm reply',
                'unseen loom reply' => 'seen loom reply',
                default => $this->last_state
            };

            $this->save();

            $this->histories()->create([
                'state' => $this->last_state,
                'account_id' => $this->account_id,
            ]);
        }
    }

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function threads()
    {
        return $this->hasMany(Thread::class);
    }

    public function notifs()
    {
        return $this->hasMany(Notif::class);
    }

    public function histories()
    {
        return $this->hasMany(LeadHistory::class);
    }

    public function looms()
    {
        return $this->hasMany(Loom::class);
    }
}
