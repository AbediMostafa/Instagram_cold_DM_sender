<?php

namespace App\Http\Controllers;

use App\Models\Account;
use App\Models\Command;
use App\Models\Lead;
use App\Models\Message;
use App\Models\Notif;
use App\Models\Thread;
use App\Services\ChangeLeadStateService;
use Illuminate\Support\Facades\DB;

class LeadController extends Controller
{
    public function index()
    {
        return Lead::query()
            ->with([
                'account:id,username',
                'category:id,title',
            ])
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
            fn() => ChangeLeadStateService::makeInstance(r('ids'), r('state'))
                ->execute(),
            "Lead's state changed successfully",
            "Problem changing lead's state"
        );
    }

    public function setCategory()
    {
        return tryCatch(
            fn() => Lead::query()
                ->whereIn('id', r('leadIds'))
                ->update([
                    'category_id' => r('categoryId'),
                ]),
            'Lead(s) updated successfully',
            'Problem updating lead(s)',
        );
    }
}
