<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Setting extends Model
{
    use HasFactory;

    protected $guarded = [];
    public $timestamps = false;

    public static array $types = [
        'number',
        'text',
        'switch',
    ];
    public static array $categories = [
        'Follow',
        'DM',
        'Templates',
        'Proxy',
        'Command',
        'Comment',
        'Like',
    ];
}
