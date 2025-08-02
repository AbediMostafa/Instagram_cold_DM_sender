<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DmPost extends Model
{
    use HasFactory;


    protected $guarded = [];
    public const UPDATED_AT = null;

    public function category(): \Illuminate\Database\Eloquent\Relations\BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function leads()
    {
        return $this->belongsToMany(Lead::class);
    }

}
