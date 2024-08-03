<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LeadHistory extends Model
{
    use HasFactory;

    protected $guarded = [];
    public $timestamps = false;

    public function lead()
    {
        return $this->belongsTo(Lead::class);
    }
}
