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
        'cold dm spintax',
        'first loom follow up spintax',
        'second loom follow up spintax',
        'third loom follow up spintax',
        'loom follow up message',
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
}
