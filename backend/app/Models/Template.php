<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Template extends Model
{
    use HasFactory;

    /***
     * just gimme more 500 usernames
     * with this format:
     * plese make me 200 instagram accounts using these words:
     * mehran keshavarz farda motors
     * you can cut keshasvarz to a word like k or kvrz and mehran to mh
     * or mhr
     * connect these words with _ or .
     * make sure words are uder 28
     * make 200 usernames for start for me
     * make sure usernames are unique
     * in php array frmat
     */


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

    public function category(): \Illuminate\Database\Eloquent\Relations\BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function tags()
    {
        return $this->morphToMany(Tag::class, 'taggable');
    }
}
