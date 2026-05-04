<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;

class AccountTemplate extends Pivot
{
    protected $table = 'account_template';

    public $incrementing = true;

    // We manage timestamps manually. created_at is set by the worker
    // when a post completes (and by the assign endpoint when a row is
    // created in 'pending' state). updated_at is bumped when stats or
    // status are refreshed.
    public $timestamps = false;

    protected $guarded = [];

    public static array $statuses = [
        'pending',
        'processing',
        'completed',
    ];

    protected $casts = [
        'stats'         => 'array',
        'created_at'    => 'datetime',
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
