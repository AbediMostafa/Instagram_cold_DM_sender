<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Account;
use Illuminate\Http\Request;

class AccountSpecController extends Controller
{
    public function index()
    {
        return Account::query()
            ->select('id', 'username', 'instagram_state')
            ->where('instagram_state', 'active')
            ->with('specs')
            ->orderBy('id')
            ->paginate(
                config('data.pagination.each_page.accounts')
            );
    }
}
