<?php

namespace App\Http\Controllers;

use App\Models\Country;
use Illuminate\Http\Request;

class CountryController extends Controller
{
    public function index()
    {
        return Country::query()
            ->select('id', 'name', 'country_code')
            ->when(request('q'), function ($query) {
                $query->where('name', likeOperator(), '%' . request('q') . '%');
            })
            ->orderBy('name')
            ->get();
    }
}
