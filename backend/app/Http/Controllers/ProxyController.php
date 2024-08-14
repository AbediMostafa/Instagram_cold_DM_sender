<?php

namespace App\Http\Controllers;

use App\Models\Proxy;
use Illuminate\Validation\Rule;

class ProxyController extends Controller
{
    public function index()
    {
        return Proxy::query()
            ->with('accounts:id,username,proxy_id,instagram_state')
            ->paginate(
                config('data.pagination.each_page.proxies')
            );
    }

    public function view()
    {
        return Proxy::query()->with('account:id,username')->find(request('id'));
    }

    public function create()
    {
        if (request('bulk_insertion')) {
            request()->validate([
                'proxies' => 'required',
            ]);
        } else {
            request()->validate([
                'ip' => ['required', 'ip',
                    Rule::unique('proxies')->where(function ($query) {
                        return $query->where('ip', request('ip'))
                            ->where('port', request('port'));
                    })
                ],
                'port' => 'required|numeric',
                'username' => 'required|string',
                'password' => 'required|string',
            ]);
        }

        return tryCatch(
            fn() => request('bulk_insertion') ? Proxy::createBulk() : Proxy::createOne()
            ,
            'Proxy created successfully',
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Proxy::query()
                ->whereIn('id', request('ids'))
                ->delete(),
            'Proxy(s) deleted successfully',
        );
    }

    public function edit()
    {
        request()->validate([
            'ip' => 'required|ip|unique:proxies,ip,' . request('id'),
            'port' => 'required|numeric',
            'username' => 'sometimes|string',
            'password' => 'sometimes|string',
            'account_id' => 'required|exists:accounts,id'
        ]);

        return tryCatch(
            fn() => Proxy::query()
                ->where('id', request('id'))
                ->update([
                    'ip' => request('ip'),
                    'port' => request('port'),
                    'username' => request('username'),
                    'password' => request('password'),
                    'account_id' => request('account_id'),
                ]),
            'Proxy updated successfully',
        );
    }
}
