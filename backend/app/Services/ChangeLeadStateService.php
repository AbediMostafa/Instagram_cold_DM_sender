<?php

namespace App\Services;

use App\Models\Command;
use App\Models\Thread;
use Illuminate\Support\Facades\DB;


class ChangeLeadStateService
{
    public $thread;
    public $threadId;
    public $lead;

    public function __construct(public $threadIds, public $state)
    {
    }

    public static function makeInstance($threadIds, $state): ChangeLeadStateService
    {
        return new ChangeLeadStateService($threadIds, $state);
    }

    public function execute()
    {
        foreach ($this->threadIds as $this->threadId) {

            DB::transaction(function () {
                $this->thread = Thread::query()->find($this->threadId);
                $this->thread->makeSeenUnseenMessages();

                $this->lead = $this->thread->lead;

                $this->handleCallBookedState();
                $this->updateLeadState();
            });
        }
    }

    public function handleCallBookedState()
    {
        if ($this->stateIs('call booked')) {

            //If lead's last state is call booked and user keeps clicking on call booked
            // it creates call booked command and displays wrong statistics in dashboard
            if ($this->lead->last_state !== 'call booked') {
                Command::query()->create([
                    'account_id' => $this->lead->account_id,
                    'lead_id' => $this->lead->id,
                    'type' => 'call booked',
                    'state' => 'success',
                ]);
            }
        }
    }

    public function updateLeadState()
    {
        if ($this->stateIs('autoreply')) {
            $this->state = match ($this->lead->last_state) {
                'unseen loom reply', 'loom follow up', 'seen loom reply', 'failed loom dm', 'call booked' => 'loom follow up',
                default => 'dm follow up'
            };
        }

        $this->lead->update([
            'last_state' => $this->state,
            'times' => 0
        ]);

        $this->lead->histories()->create([
            'state' => $this->state,
            'account_id' => $this->lead->account_id,
        ]);
    }

    public function stateIs($state)
    {
        return $this->state == $state;
    }

}
