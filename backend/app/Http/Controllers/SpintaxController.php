<?php

namespace App\Http\Controllers;

use App\Models\Spintax;
use Illuminate\Http\Request;

class SpintaxController extends Controller
{

    public function index()
    {
        return Spintax::query()
            ->select('id', 'name', 'type', 'is_active', 'text')
            ->orderBy('type')
            ->paginate(
                config('data.pagination.each_page.spintaxes')
            );
    }

    public function view()
    {
        return Spintax::query()
            ->select('id', 'name', 'type', 'is_active', 'text')
            ->find(r('id'));
    }

    public function create()
    {
        r()->validate(
            ['data.name' => 'unique:spintaxes,name'],
            ['data.name.unique' => 'The name must be unique. This name is already taken.']
        );

        return tryCatch(
            fn() => Spintax::query()->create(r('data'))
            , 'Spintax created successfully'
        );
    }
}
