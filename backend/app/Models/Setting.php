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
        'Post',
        'General'
    ];

    public static function getValue($key, $default = null)
    {
        $record = Setting::query()->where('key', $key)->first();

        return $record ? $record->value : $default;
    }

    public static function setValue(string $key, $value, string $type = 'text', string $description = null): void
    {
        self::query()->updateOrCreate(
            ['key' => $key], // condition
            [
                'value' => $value,
                'type' => $type,
                'description' => $description,
            ]
        );
    }
}
