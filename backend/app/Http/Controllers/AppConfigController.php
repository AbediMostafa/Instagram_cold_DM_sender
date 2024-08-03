<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class AppConfigController extends Controller
{
    public function index()
    {
        return config('data');
    }
}
