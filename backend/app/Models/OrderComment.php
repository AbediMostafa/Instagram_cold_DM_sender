<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OrderComment extends Model
{
    use HasFactory;
    protected $guarded =[];

    public function setStatusTo($status)
    {
        $this->status = $status;
        $this->save();
    }
}
