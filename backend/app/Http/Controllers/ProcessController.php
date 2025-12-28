<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Process;
use Carbon\Carbon;
use Illuminate\Http\Request;

class ProcessController extends Controller
{

    public function index()
    {
        return Process::query()
            ->with('workflow:id,title')
            ->orderBy('id', 'desc')->paginate(75);
    }

    public function check()
    {
        Process::where('status', '!=', 'terminated')
            ->where('last_checked_at', '<', Carbon::now()->subMinutes(10))
            ->update([
                'status' => 'terminated',
            ]);
    }


    public function verify()
    {
        $process = Process::updateOrCreate(
            ['pid' => (int)r('pid')],
            ['last_checked_at' => Carbon::now('Asia/Tehran')]
        )->refresh()->load([
            'workflow:id,title,service_id',
            'workflow.service:id,title,service',
            'workflow.modules'
        ]);

        $service = $process->workflow?->service;
        $shouldRun = false;

        if ($service) {
            $shouldRun = $service->shouldRun();
        }

        $process->should_run = $shouldRun;

        return $process;

    }

    public function update()
    {
        return tryCatch(
            fn() => Process::query()->where('id', r('id'))
                ->update([
                    'workflow_id' => r('workflow_id')
                ]),
            'Process updated successfully'
        );
    }

    public function getInitialData(): array
    {
        return [
            'stopped_statuses' => Process::$stoppedStatuses,
        ];

    }

    public function delete()
    {
        return tryCatch(
            fn() => Process::query()->whereIn('id', r('ids'))->delete(),
            'Process deleted successfully'
        );
    }

    public function toggleProcess()
    {

        $process = Process::query()->find(r('id'));

        abort_if($process->is('terminated'), 422, 'Terminated process cant be started nor stopped');

        return tryCatch(
            fn() => $process->setTo($process->is('running') ? 'stopped' : 'running'),
            'Process status changed successfully'
        );

    }

    public function setWorkflow()
    {
        return tryCatch(
            fn() => Process::query()->whereIn('id', r('ids'))->update(['workflow_id' => r('workflow_id')]),
            'Workflow changed successfully'
        );
    }

    public function setStatus()
    {
        return tryCatch(
            fn() => Process::query()->whereIn('id', r('ids'))->update(['status' => r('status')]),
            'Workflow changed successfully'
        );
    }
}
