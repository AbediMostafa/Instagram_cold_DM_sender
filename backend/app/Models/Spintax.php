<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Spintax extends Model
{
    use HasFactory;
    protected $guarded = [];

    public static array $types = [
      'cold dm',
      'first dm follow up',
      'second dm follow up',
      'third dm follow up',
    ];
}
