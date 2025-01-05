<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Template extends Model
{
    use HasFactory;


    protected $guarded = [];
    const UPDATED_AT = null;

    public static array $types = [
        'name',
        'username',
        'bio',
        'avatar',
        'carousel',
        'image-post',
        'video-post',
    ];

    public static array $subTypes = [
        'image',
        'video',
    ];

    public function accounts()
    {
        return $this->belongsToMany(Account::class);
    }

    public function color()
    {
        return $this->belongsTo(Color::class);
    }

    public function category()
    {
        return $this->belongsTo(Category::class);
    }

    public function tags()
    {
        return $this->morphToMany(Tag::class, 'taggable');
    }
}
