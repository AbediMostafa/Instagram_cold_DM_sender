<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class TikTokTag extends Model
{
    use HasFactory;

    protected $fillable = ['title'];

    public function tikTokLinks(): BelongsToMany
    {
        return $this->belongsToMany(
            TikTokLink::class,
            'tik_tok_link_tag',
            'tik_tok_tag_id',
            'tik_tok_link_id'
        );
    }
}
