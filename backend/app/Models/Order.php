<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    use HasFactory;

    protected $guarded = [];

    static $statuses = ['Pending', 'In progress', 'Completed', 'Canceled', 'Unknown'];
    static $activeStatuses = ['Pending', 'In progress'];

    protected function serializeDate(\DateTimeInterface $date)
    {
        return Carbon::instance($date)->format('m-d H:i');
    }

    public function actions()
    {
        return $this->hasMany(OrderAction::class, 'order_id', 'id');
    }

    public function service()
    {
        return $this->belongsTo(Service::class);
    }

    public function getCompletedCount()
    {
        return $this->actions()->whereIn('status', ['sent', 'failed'])->count();
    }

    public function getRemains()
    {
        return max(0, $this->total_count - $this->completed_count);
    }

    public function setStatusTo($status)
    {
        $this->status = $status;
        return $this->save();
    }

    public function changeProcessingToFree()
    {
        $this->setStatusTo('In progress');

        $this->actions()->where('status', 'processing')->update([
            'status' => 'free',
            'account_id' => null
        ]);
    }
}
