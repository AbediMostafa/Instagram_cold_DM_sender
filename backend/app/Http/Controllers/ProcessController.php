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
        $query = Process::query()
            ->with('workflow:id,title')
            ->orderBy('id', 'desc');

        if (request('server_ip')) {
            $query->byServer(request('server_ip'));
        }

        return $query->paginate(75);
    }

    public function check()
    {
        Process::where('status', '!=', 'terminated')
            ->where('last_checked_at', '<', Carbon::now()->subMinutes(10))
            ->update([
                'status' => 'terminated',
            ]);
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
        $serverIps = Process::query()
            ->select('server_ip')
            ->distinct()
            ->pluck('server_ip')
            ->toArray();

        return [
            'stopped_statuses' => Process::$stoppedStatuses,
            'server_ips' => $serverIps,
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
            'Status changed successfully'
        );
    }

    public function getServers()
    {
        return Process::query()
            ->select('server_ip')
            ->distinct()
            ->pluck('server_ip');
    }

    // Server-based actions

    public function setStatusByServers()
    {
        $serverIps = r('server_ips', []);
        $status = r('status');

        abort_if(empty($serverIps), 422, 'Please select at least one server');
        abort_if(!in_array($status, ['running', 'stopped']), 422, 'Invalid status');

        return tryCatch(
            fn() => Process::query()
                ->whereIn('server_ip', $serverIps)
                ->where('status', '!=', 'terminated')
                ->update(['status' => $status]),
            'Status changed for all processes on selected servers'
        );
    }

    public function setWorkflowByServers()
    {
        $serverIps = r('server_ips', []);
        $workflowId = r('workflow_id');

        abort_if(empty($serverIps), 422, 'Please select at least one server');

        return tryCatch(
            fn() => Process::query()
                ->whereIn('server_ip', $serverIps)
                ->update(['workflow_id' => $workflowId]),
            'Workflow changed for all processes on selected servers'
        );
    }

    public function deleteByServers()
    {
        $serverIps = r('server_ips', []);

        abort_if(empty($serverIps), 422, 'Please select at least one server');

        return tryCatch(
            fn() => Process::query()
                ->whereIn('server_ip', $serverIps)
                ->delete(),
            'All processes deleted on selected servers'
        );
    }

    public function getServerStats()
    {
        return Process::query()
            ->selectRaw('server_ip, status, COUNT(*) as count')
            ->groupBy('server_ip', 'status')
            ->get()
            ->groupBy('server_ip')
            ->map(function ($items) {
                return $items->pluck('count', 'status');
            });
    }
}
