<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Category extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'description',
    ];

    public function accounts()
    {
        return $this->hasMany(Account::class);
    }

    public function leads()
    {
        return $this->hasMany(Lead::class);
    }

    public function commands()
    {
        return $this->hasMany(Command::class);
    }

    public function threads()
    {
        return $this->hasMany(Thread::class);
    }

    public function templates()
    {
        return $this->hasMany(Template::class);
    }

    public function spintexes()
    {
        return $this->hasMany(Spintax::class);
    }
}
