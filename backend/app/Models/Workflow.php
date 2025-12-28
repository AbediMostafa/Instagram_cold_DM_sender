<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Workflow extends Model
{
    use HasFactory;

    protected $guarded = [];
    const UPDATED_AT = null;
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i',
    ];

    protected static function booted()
    {
        static::deleting(function ($workflow) {
            $workflow->modules()->detach();
        });
    }

    public function service()
    {
        return $this->belongsTo(Service::class);
    }

    public function modules()
    {
        return $this->belongsToMany(Module::class, 'workflow_module', 'workflow_id', 'module_id');
    }

}
