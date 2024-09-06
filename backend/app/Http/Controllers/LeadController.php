<?php

namespace App\Http\Controllers;

use App\Models\Lead;
use App\Models\Message;
use App\Models\Notif;
use App\Models\Thread;
use Illuminate\Support\Facades\DB;

class LeadController extends Controller
{
    public function index()
    {
        return Lead::query()
            ->with('account:id,username')
            ->paginate(
                config('data.pagination.each_page.leads')
            );
    }


    public function view()
    {
        return Lead::query()->with('account:id,username')->find(r('id'));
    }

    public function create()
    {
        r()->validate([
            'username' => 'required|unique:leads'
        ]);

        return tryCatch(
            fn() => Lead::query()->create([
                'username' => r('username'),
            ]),
            'Lead created successfully',
        );
    }


    public function delete()
    {
        return tryCatch(
            fn() => Lead::query()
                ->whereIn('id', r('ids'))
                ->delete(),
            'Lead(s) deleted successfully',
        );
    }

    public function edit()
    {
        r()->validate([
            'username' => 'required|unique:leads,username,' . r('id')
        ]);

        return tryCatch(
            fn() => Lead::query()
                ->where('id', r('id'))
                ->update([
                    'username' => r('username'),
                ]),
            'Lead updated successfully',
        );
    }

    public function changeState()
    {
        return tryCatch(
            function () {
                DB::transaction(function () {

                    $message = Message::find(r('messageId'));

                    $message->update(['state' => 'seen']);

                    $lead = Thread::find(r('threadId'))
                        ->lead;

                    if (r('state') == 'call booked') {

                        //If lead's last state is call booked and user keeps clicking on call booked
                        // it creates call booked command and displays wrong statistics in dashboard
                        if ($lead->last_state !== 'call booked') {
                            $message->command()
                                ->create([
                                    'account_id' => $message->thread->account_id,
                                    'lead_id' => $message->thread->lead_id,
                                    'type' => 'call booked',
                                    'state' => 'success',
                                ]);
                        }
                    }

                    $lead->update([
                        'last_state' => r('state'),
                        'times' => 0
                    ]);

                    $lead->histories()->create([
                        'state' => r('state'),
                        'account_id' => $lead->account_id,
                    ]);
                });
            },
            "Lead's state changed successfully",
            "Problem changing lead's state"
        );
    }

}
