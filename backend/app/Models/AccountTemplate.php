<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;

class AccountTemplate extends Pivot
{
    protected $table = 'account_template';

    public $incrementing = true;

    // We manage updated_at manually when stats are refreshed; there is no created_at column.
    public $timestamps = false;

    protected $guarded = [];

    public static array $statuses = [
        'pending',
        'processing',
        'completed',
    ];

    protected $casts = [
        'stats'         => 'array',
        'posted_at'     => 'datetime',
        'updated_at'    => 'datetime',
        'like_count'    => 'integer',
        'comment_count' => 'integer',
        'view_count'    => 'integer',
        'save_count'    => 'integer',
        'repost_count'  => 'integer',
    ];

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function template()
    {
        return $this->belongsTo(Template::class);
    }
}
