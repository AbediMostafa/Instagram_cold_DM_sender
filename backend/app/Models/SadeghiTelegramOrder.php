<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SadeghiTelegramOrder extends Model
{
    use HasFactory;

    protected $guarded =[];

    public function setStatusTo($status)
    {
        $this->status = $status;
        return $this->save();
    }
}
