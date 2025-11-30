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
    ];

    public static function getValue($key, $default = null)
    {
        $record = Setting::query()->where('key', $key)->first();

        return $record ? $record->value : $default;
    }

    public static function setValue(string $key, $value, string $type = 'text', string $description = null): void
    {
        // Check if a record with the given key exists
        $setting = self::query()->where('key', $key)->first();

        // Set or update fields
        $setting->value = $value;
        $setting->type = $type;
        $setting->description = $description;

        $setting->save();
    }
}
