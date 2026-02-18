<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class TikTokLink extends Model
{
    use HasFactory;
    protected $guarded =[];

    protected function serializeDate(\DateTimeInterface $date)
    {
        return Carbon::instance($date)->format('m-d H:i');
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(
            TikTokTag::class,
            'tik_tok_link_tag',
            'tik_tok_link_id',
            'tik_tok_tag_id'
        );
    }

}
