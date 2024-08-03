<?php

namespace App\Http\Controllers;

use App\Models\Account;
use Illuminate\Http\Request;

class CliController extends Controller
{

    public function index()
    {
        return Account::query()->find(r('account_id'))
            ->clis;
    }
}
