<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;

class AuthController extends Controller
{
    public function login()
    {
        $credentials = r()->only('email', 'password');

        return Auth::attempt($credentials) ?
            jsonSuccess('You logged in successfully', ["user" => Auth::user()->returnable()]) :
            jsonError('Invalid credentials');
    }

    public function signOut()
    {
        Auth::logout();
    }

    public function register()
    {
        User::query()->create([
            'name'=>'admin',
            'email'=>'admin@admin.com',
            'password'=>Hash::make('123!@#')
        ]);
    }

}
