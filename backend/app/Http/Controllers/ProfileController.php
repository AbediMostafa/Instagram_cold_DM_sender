<?php

namespace App\Http\Controllers;

use App\Classes\ProfileMaker;
use App\Classes\ProfileMakerV2;
use App\Models\Account;
use App\Models\Profile;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class ProfileController extends Controller
{
    public function index()
    {
        return Profile::query()
            ->with(['accounts:id,username,profile_id,instagram_state', 'proxy:id,ip'])
            ->when(
                r('text'),
                function ($_) {
                    if (r('type') === 'proxy') {
                        $_->whereHas('proxy', fn($__) => $__->where('ip', 'like', '%' . r('text') . '%'));
                    }

                    if (r('type') === 'account') {
                        $_->whereHas('accounts', fn($__) => $__->where('username', 'like', '%' . r('text') . '%'));
                    }

                    if (r('type') === 'profile') {
                        $_->where('title', 'like', '%' . r('text') . '%');
                    }
                }
            )
            ->paginate(
                config('data.pagination.each_page.profiles')
            );
    }

    public function view()
    {
        return Profile::query()->with('accounts:id,username')->find(request('id'));
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'folder' => 'required|string|max:255',
            'accounts' => 'required|array',
            'accounts.*' => 'required|exists:accounts,id',
        ]);

        // Check if all selected accounts have the same proxy_id as the one provided
        $accountsWithDifferentProxy = Account::query()
            ->whereIn('id', r('accounts'))
            ->where('proxy_id', '!=', r('proxy_id'))
            ->exists();

        if ($accountsWithDifferentProxy) {
            return jsonError('All selected accounts must have the same proxy_id as the provided proxy.');
        }

        return tryCatch(
            function () {
                DB::transaction(function () {
                    $profile = Profile::create(r()->only(['title', 'folder', 'profile_id', 'proxy_id']));

                    Account::query()->whereIn('id', r('accounts'))
                        ->get()
                        ->each(function ($account) use ($profile) {
                            $account->profile_id = $profile->id;
                            $account->save();
                        });
                });

            },
            'Profile created successfully'
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Profile::query()
                ->whereIn('id', request('ids'))
                ->get()
                ->each(function($profile){
                    $profile->deleteRecords();
                    sleep(3);
                })
            ,
            'Profile(s) deleted successfully'
        );
    }

    public function edit(Request $request)
    {
        $validated = $request->validate([
            'id' => 'required|exists:profiles,id',
            'title' => 'required|string',
            'folder' => 'required|string',
            'profile_id' => 'required|string',
            'proxy_id' => 'nullable|exists:proxies,id',
            'accounts' => 'array',
            'accounts.*' => 'exists:accounts,id',
        ]);

        $profile = Profile::find($validated['id']);
        $profile->update($validated);

        // Handle the relationship with accounts if necessary
        // $profile->accounts()->sync($validated['accounts']);

        return response()->json(['message' => 'Profile updated successfully']);
    }

    public function makeAndAssignProfiles()
    {
        return tryCatch(
            fn() => ProfileMakerV2::getInstance(r('ids'))->iterateAndAssignProfile(),
            'Profile assigned successfully',
        );
    }

    public function assignToAccountAPI()
    {
        r()->validate([
            'username' => 'required',
            'password' => 'required',
            'account_id' => 'nullable|integer|exists:accounts,id',
        ]);

        $credentials = [
            'email' => r('username'),
            'password' => r('password'),
        ];

        if (!Auth::attempt($credentials)) {
            return response()->json(['message' => 'Invalid credentials'], 422);
        }

        return tryCatch(
            fn() => ProfileMakerV2::getInstance(r('ids'))->iterateAndAssignProfile(),
            'Profile assigned successfully',
        );
    }
}
