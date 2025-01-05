<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function getUsersByName()
    {
        return User::query()
            ->select('id', 'name')
            ->get();
    }
}
