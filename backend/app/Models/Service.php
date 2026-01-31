<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Service extends Model
{
    use HasFactory;

    protected $guarded = [];
    const UPDATED_AT = null;

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i',
    ];


    public function workflows()
    {
        return $this->hasMany(Workflow::class);
    }

    public function orders()
    {
        return $this->hasMany(Order::class);
    }

}
