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

    public function duoWorkflows(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(DuoWorkFlow::class, 'order_id');
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

        $this->actions()
            ->where('status', '!=', 'sent')
            ->update([
                'status' => 'free',
                'account_id' => null
            ]);
    }

    public function is($status)
    {
        return $this->status == $status;
    }

    public function makeShareActions()
    {
        $remaining = $this->total_count;
        $actions = [];

        while ($remaining > 0) {
            // CHUNK_SIZE would be the size of group
            $count = min(OrderAction:: SHARE_CHUNK_SIZE, $remaining);

            $actions[] = [
                'order_id' => $this->id,
                'type' => $this->service_type ?? 'share',
                'count' => $count,
            ];

            $remaining -= $count;
        }

        OrderAction::query()->insert($actions);

        return $this;
    }

    public static function getPendings()
    {
        return Order::query()
            ->whereIn('status', Order::$activeStatuses)
            ->where(function ($query) {

                // Pending order with no actions yet
                $query->where(function ($q) {
                    $q->where('status', 'Pending')
                        ->whereDoesntHave('actions');
                })

                    // Has expired pending actions
                    ->orWhereHas('actions', function ($q) {
                        $q->where('status', 'processing')
                            ->where('updated_at', '<', now()->subMinutes(OrderAction::EXPIRATION_TIME));
                    })

                    // OR has free actions
                    ->orWhereHas('actions', function ($q) {
                        $q->where('status', 'free');
                    });

            })
            ->orderBy('id')
            ->get();
    }

    public function getExpiredActions($limit)
    {
        return $this->actions()
            ->where('status', 'processing')
            ->where('updated_at', '<', now()->subMinutes(OrderAction::EXPIRATION_TIME))
            ->orderBy('id')
            ->lockForUpdate()
            ->limit($limit)
            ->get();
    }

    public function getFreeActions($limit, $status = 'free')
    {
        return $this->actions()
            ->where('status', $status)
            ->orderBy('id')
            ->lockForUpdate()
            ->limit($limit)
            ->get();
    }
}
