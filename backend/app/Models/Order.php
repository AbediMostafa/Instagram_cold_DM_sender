<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    use HasFactory;

    protected $guarded = [];

    public function comments()
    {
        return $this->hasMany(OrderComment::class, 'order_id', 'id');
    }

    public function getRemains()
    {
        $remains = $this->total_count - $this->completed_count;
        return 0 ? $remains < 0 : $remains;
    }
}
