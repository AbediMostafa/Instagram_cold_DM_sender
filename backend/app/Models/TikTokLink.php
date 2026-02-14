<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TikTokLink extends Model
{
    use HasFactory;
    protected $guarded =[];

    protected function serializeDate(\DateTimeInterface $date)
    {
        return Carbon::instance($date)->format('m-d H:i');
    }
}
