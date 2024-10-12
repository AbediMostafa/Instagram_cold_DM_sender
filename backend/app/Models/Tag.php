<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Tag extends Model
{
    use HasFactory;

    const UPDATED_AT = null;

    protected $guarded =[];

    public function leads()
    {
        return $this->morphedByMany(Lead::class, 'taggable');
    }

    public function accounts()
    {
        return $this->morphedByMany(Account::class, 'taggable');
    }
}
