<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Workflow;
use Illuminate\Http\Request;

class WorkflowController extends Controller
{
    public function index()
    {
        return Workflow::query()
            ->with('service:id,service')
            ->with('modules:id,title')
            ->orderBy('id', 'desc')->paginate(75);
    }

    public function create()
    {
        return tryCatch(
            function () {
                $workflow = Workflow::query()
                    ->create([
                        'title' => r('title'),
                        'service_id' => r('service_id'),
                    ]);

                if ($modules = r('modules')) {
                    $workflow->modules()->sync($modules);
                }
            },
            'Workflow created successfully'
        );
    }

    public function update()
    {
        return tryCatch(
            function () {
                $workflow = Workflow::findOrFail(r('id'));
                $workflow->update([
                    'title' => r('title'),
                    'service_id' => r('service_id'),
                ]);
                if ($modules = r('modules')) {
                    $workflow->modules()->sync($modules); // <-- update many-to-many
                }

            },
            'Workflow updated successfully'
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Workflow::query()
                ->whereIn('id', r('ids'))
                ->delete(),

            'Workflow(s) Deleted Successfully'
        );
    }
}
