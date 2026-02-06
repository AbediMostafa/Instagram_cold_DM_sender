<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OrderComment extends Model
{
    use HasFactory;

    protected $guarded = [];

    public function setStatusTo($status)
    {
        $this->status = $status;
        $this->save();
    }

    public function order()
    {
        return $this->belongsTo(Order::class);
    }

    public static function getCommentToExecute($orderId)
    {
        return self::query()
            ->where('order_id', $orderId)
            ->where('status', 'free')
            ->orderBy('id')
            ->first();
    }
}
