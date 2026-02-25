<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Process extends Model
{
    use HasFactory;

    protected $guarded = [];
    const UPDATED_AT = null;

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i',
        'last_checked_at' => 'datetime:Y-m-d H:i',
    ];

    public $protectedStatuses = ['running', 'stopped', 'idle'];

    public static $stoppedStatuses = ['stopped', 'idle', 'terminated'];

    public function workflow()
    {
        return $this->belongsTo(Workflow::class);
    }

    public function cantBeDeleted()
    {
        return in_array($this->status, $this->protectedStatuses);
    }

    public function is($status)
    {
        return $this->status == $status;
    }

    public function setTo($status)
    {
        $this->status = $status;
        $this->save();
    }

    public function scopeByServer($query, $serverIp)
    {
        return $query->where('server_ip', $serverIp);
    }
}
