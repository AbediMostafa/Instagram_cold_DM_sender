<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Service extends Model
{
    use HasFactory;

    protected $guarded = [];
    const UPDATED_AT = null;

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i',
    ];

    static $staticServices = ['account_profiler'];


    public function workflows()
    {
        return $this->hasMany(Workflow::class);
    }

    public function orders()
    {
        return $this->hasMany(Order::class);
    }

    /**
     * Check if service has any active orders
     * (pending or in_progress)
     */
    public function hasActiveOrders(): bool
    {
        return $this->orders()
            ?->whereIn('status', Order::$activeStatuses)
            ->exists();
    }

    /**
     * Business rule:
     * account_profiler should always run
     */
    public function shouldRun(): bool
    {
        return in_array($this->service, self::$staticServices) || $this->hasActiveOrders();
    }
}
