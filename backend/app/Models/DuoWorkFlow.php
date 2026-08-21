<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DuoWorkFlow extends Model
{
    use HasFactory;
    protected $guarded=[];

    protected $table = 'duo_workflows';
    const UPDATED_AT = null;


    public function order(): \Illuminate\Database\Eloquent\Relations\BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function actions()
    {
        return $this->hasMany(OrderAction::class, 'duo_workflow_id');
    }
}
