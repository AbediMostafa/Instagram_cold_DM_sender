<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Service;
use Illuminate\Http\Request;

class ServiceController extends Controller
{
    public function index()
    {
        return Service::query()->orderBy('id', 'desc')->paginate(75);
    }

    public function create()
    {
        return tryCatch(
            fn() => Service::query()->create(r()->all()),
            'Service created successfully'
        );
    }

    public function search()
    {
        return Service::query()
            ->where('title', 'ilike', '%' . request('q') . '%')
            ->get();
    }

    public function update()
    {

        return tryCatch(
            fn() => Service::query()
                ->where('id', r('id'))
                ->update([
                    'title' => r('title'),
                    'service' => r('service'),
                    'description' => r('description'),
                ]),

            'Service Updated Successfully'
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Service::query()
                ->whereIn('id', r('ids'))
                ->delete(),

            'Service Deleted Successfully'
        );

    }
}
