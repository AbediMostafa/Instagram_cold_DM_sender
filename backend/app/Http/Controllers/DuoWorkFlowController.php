<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Cli;
use App\Models\DuoWorkFlow;
use App\Models\Mobile;
use App\Models\Order;
use App\Models\OrderAction;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class DuoWorkFlowController extends Controller
{

    public function start()
    {
        Log::info('START ' . microtime(true));
        foreach (Order::getPendings() as $order) {
            $response = DB::transaction(function () use ($order) {

                $mobile = Mobile::query()
                    ->where('duo_id', r('phone_id'))
                    ->first();

                if ($order->is('Pending') && !$order->actions()->exists()) {
                    Log::info("{$mobile?->name} -- Order number {$order->id} is pending");
                    $order->makeShareActions()->setStatusTo('In progress');
                }

                //First reclaim expired actions.
                $expiredActions = $order->getExpiredActions(OrderAction::SHARE_ACTIONS_PER_RUN);
                $expiredCount = $expiredActions->count();

                Log::info("{$mobile?->name} -- {$expiredCount} Expired actions exists");

                $remaining = OrderAction::SHARE_ACTIONS_PER_RUN - $expiredCount;

                $freeActions = collect();

                if ($remaining > 0) {
                    $freeActions = $order->getFreeActions($remaining);
                    Log::info("{$mobile?->name} -- {$freeActions->count()} Free actions claimed");
                }

                if ($expiredActions->isEmpty() && $freeActions->isEmpty()) {
                    return null;
                }

                $workFlow = $order->duoWorkFlows()->create([
                    'mobile_id' => $mobile?->id,
                    'task_id' => r('task_id'),
                ]);

                $expiredActions->each(fn(OrderAction $action) => $action->updateWorkflow($workFlow));
                $freeActions->each(fn(OrderAction $action) => $action->updateWorkflow($workFlow));

                return [
                    'action_count' => $expiredCount + $freeActions->count(),
                    'url' => $order->target_link,
                    'workflow_id' => $workFlow->id,
                ];
            });

            Log::info('RETURN ' . microtime(true));

            if ($response !== null) {
                return $response;
            }
        }
        return -1;
    }

    public function getUrl()
    {
        $workFlow = DuoWorkFlow::query()->find(r('workflow_id'));
        if (!$workFlow)
            return -1;

        return $workFlow->order->target_link;
    }

    public function getActionCount()
    {
        $workFlow = DuoWorkFlow::query()->find(r('workflow_id'));
        if (!$workFlow)
            return -1;

        return $workFlow->actions()->count();
    }

    public function groupClick()
    {
        $workFlow = DuoWorkFlow::query()->find(r('workflow_id'));
        if (!$workFlow)
            return -1;

        $executeAction = function ($action, $type) use ($workFlow) {

            $action->updateWorkflow($workFlow, 'sent');

            Log::info("$type action : {$action->id} workflow : {$workFlow->id} Sent");

            $order = $action->order;
            $order->increment('completed_count', OrderAction::SHARE_CHUNK_SIZE);

            if (
                $order->actions()->exists() &&
                $order->actions()->whereNot('status', 'sent')->doesntExist()
            ) {
                $order->update([
                    'status' => 'Completed',
                ]);
            }

            return $action->id;
        };

        $action = $workFlow->actions()
            ->orderBy('id')
            ->where('status', 'processing')
            ->first();

        //First check for this workflow's actions
        if ($action) {
            return $executeAction($action, 'Processing');
        }

        $expiredActions = $workFlow->order->getExpiredActions(1);

        //Next check for expired actins
        if (!$expiredActions->isEmpty()) {
            return $executeAction($expiredActions->first(), 'Expired');
        }

        $freeActions = $workFlow->order->getFreeActions(1);

        //Then check for free actions
        if (!$freeActions->isEmpty()) {
            return $executeAction($freeActions->first(), 'Free');
        }

        //Get other workflow's action
        $otherWorkflowsActions = $workFlow->order->getFreeActions(1, 'processing');

        //Then check for free actions
        if (!$otherWorkflowsActions->isEmpty()) {
            return $executeAction($otherWorkflowsActions->first(), 'Other workflow');
        }
    }

    public function changeAccount()
    {
        $mobile = Mobile::query()
            ->where('duo_id', r('phone_id'))
            ->first();

        $nextAccount = $mobile->getNextAccount();

        if ($nextAccount) {
            Log::info("Account changed to {$nextAccount->username}");
            return $nextAccount->username;
        }

        return -1;
    }
}
