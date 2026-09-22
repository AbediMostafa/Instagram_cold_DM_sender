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
        foreach (Order::getPendings() as $order) {
            $response = DB::transaction(function () use ($order) {

                $mobile = Mobile::query()
                    ->where('duo_id', r('phone_id'))
                    ->first();

                if ($order->is('Pending') && !$order->actions()->exists()) {
                    Log::channel('workflow')->info("{$mobile?->name} -- Order number {$order->id} is pending");
                    $order->makeShareActions()->setStatusTo('In progress');
                }

                //First reclaim expired actions.
                $expiredActions = $order->getExpiredActions(OrderAction::SHARE_ACTIONS_PER_RUN);
                $expiredCount = $expiredActions->count();

                Log::channel('workflow')->info("{$mobile?->name} -- {$expiredCount} Expired actions exists");

                $remaining = OrderAction::SHARE_ACTIONS_PER_RUN - $expiredCount;

                $freeActions = collect();

                if ($remaining > 0) {
                    $freeActions = $order->getFreeActions($remaining);
                    Log::channel('workflow')->info("{$mobile?->name} -- {$freeActions->count()} Free actions claimed");
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

        if (!$workFlow) {
            return response()->json([
                'status' => 'error',
                'message' => 'Workflow not found',
            ], 404);
        }

        return DB::transaction(function () use ($workFlow) {

            $order = $workFlow->order;

            // Get all actions belonging to this workflow
            // that haven't been sent yet.
            $actions = $workFlow->actions()
                ->where('status', 'processing')
                ->lockForUpdate()
                ->get();

            if ($actions->isEmpty()) {
                return response()->json([
                    'status' => 'success',
                    'message' => 'No processing actions found',
                    'workflow_id' => $workFlow->id,
                    'action_count' => 0,
                ]);
            }

            $actionIds = $actions->pluck('id');

            // Mark ALL workflow actions as sent in one query
            OrderAction::query()
                ->whereIn('id', $actionIds)
                ->update([
                    'status' => 'sent',
                    'updated_at' => now(),
                ]);

            $actionCount = $actions->count();

            // Increment completed count by actual number of actions
            $order->increment(
                'completed_count',
                $actionCount * OrderAction::SHARE_CHUNK_SIZE
            );

            Log::channel('workflow')->info("$actionCount actions completed");

            // Check if every action for this order is now sent
            $hasUnsentActions = $order->actions()
                ->where('status', '!=', 'sent')
                ->exists();

            if (!$hasUnsentActions) {
                $order->update([
                    'status' => 'Completed',
                ]);
            }

            Log::channel('workflow')->info(
                "Workflow {$workFlow->id} completed. " .
                "{$actionCount} actions marked as sent. " .
                "Order {$order->id}"
            );

            return response()->json([
                'status' => 'success',
                'workflow_id' => $workFlow->id,
                'action_count' => $actionCount,
                'order_id' => $order->id,
                'completed_count' => $order->fresh()->completed_count,
                'order_status' => $order->fresh()->status,
            ]);
        });

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

    public function fail()
    {

        $workFlow = DuoWorkFlow::query()->find(r('workflow_id'));

        if (!$workFlow)
            return -1;

        return $workFlow->order->fail(r('reason'));
    }
}
