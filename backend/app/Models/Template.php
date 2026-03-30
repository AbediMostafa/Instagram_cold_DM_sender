<?php

namespace App\Models;

use Carbon\Carbon;
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
        'name-username',
    ];

    public static array $subTypes = [
        'image',
        'video',
    ];

    public function accounts()
    {
        return $this->belongsToMany(Account::class);
    }

    public function leads()
    {
        return $this->belongsToMany(Lead::class);
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

    public static function createBulk()
    {
        $lines = explode("\n", request('text'));
        $existsAccounts = '';

        foreach ($lines as $line) {

            if ($line === '') {
                continue;
            }

            if (r('type') == "name-username") {
                $parts = explode(',', $line);
                $text = $parts[0];
                $caption = $parts[1];
            } else {
                $text = $line;
                $caption = null;
            }

            $templateExists = Template::query()
                ->whereType(r('type'))
                ->whereText($text)
                ->whereCaption($caption)
                ->exists();

            if ($templateExists) {
                $existsAccounts .= $text . ':' . $caption . "\n";
                continue;
            }

            $accountObj = Template::query()->create([
                'text' => $text,
                'caption' => $caption,
                'type' => r('type'),
                'created_at' => Carbon::now(),
            ]);

            !empty(r('tags')) && $accountObj->tags()->attach(r('tags'));
        }

        abort_if($existsAccounts, 403, 'These templates already exists :' . "\n" . $existsAccounts);
        return true;
    }

    public static function createOne()
    {
        $template = Template::query()->create([
            'text' => r('text'),
            'caption' => r('name'),
            'type' => r('type'),
        ]);

        return $template;
    }
}
