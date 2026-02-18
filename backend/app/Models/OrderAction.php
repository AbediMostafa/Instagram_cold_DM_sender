<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class OrderAction extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $table = 'order_actions';

    const TYPES = [
        'comment',
        'view_story',
        'view_all_stories',
        'save_post',
    ];

    const STATUSES = [
        'free',
        'processing',
        'sent',
        'failed',
    ];

    protected function serializeDate(\DateTimeInterface $date)
    {
        return Carbon::instance($date)->format('m-d H:i');
    }

    public function order()
    {
        return $this->belongsTo(Order::class);
    }

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function setStatusTo($status)
    {
        $this->status = $status;
        return $this->save();
    }

    public function markAsProcessing($accountId)
    {
        $this->status = 'processing';
        $this->account_id = $accountId;
        return $this->save();
    }

    public function markAsSent()
    {
        $this->status = 'sent';
        return $this->save();
    }

    public function resetToFree()
    {
        $this->status = 'free';
        $this->account_id = null;
        return $this->save();
    }

    public static function isValidType($type)
    {
        return in_array($type, self::TYPES);
    }

    public static function isValidStatus($status)
    {
        return in_array($status, self::STATUSES);
    }
}
