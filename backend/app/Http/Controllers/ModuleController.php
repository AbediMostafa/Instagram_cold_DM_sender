<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Module;
use Illuminate\Http\Request;

class ModuleController extends Controller
{
    public function index()
    {
        return Module::query()
            ->with('workflows:id,title')
            ->orderBy('id', 'desc')->paginate(75);
    }

    public function search()
    {
        return Module::query()
            ->where('title', 'like', '%' . request('q') . '%')
            ->get();
    }

    public function create()
    {
        return tryCatch(
            fn() => Module::query()
                ->create(r()->except('workflow_id')),
            'Module created successfully'
        );

    }

    public function update()
    {
        return tryCatch(
            fn() => Module::query()
                ->where('id', r('id'))
                ->update([
                    'title' => r('title'),
                    'module_path' => r('module_path'),
                    'class_name' => r('class_name'),
                    'priority' => r('priority'),
                ]),
            'Module updated successfully'
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Module::query()
                ->whereIn('id', r('ids'))
                ->delete(),

            'Module(s) Deleted Successfully'
        );
    }
}
