<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Module extends Model
{
    use HasFactory;

    protected $guarded = [];
    const UPDATED_AT = null;

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i',
    ];

    protected static function booted()
    {
        static::deleting(function ($module) {
            $module->workflows()->detach();
        });
    }

    public function workflows()
    {
        return $this->belongsToMany(Workflow::class,'workflow_module');
    }

}
