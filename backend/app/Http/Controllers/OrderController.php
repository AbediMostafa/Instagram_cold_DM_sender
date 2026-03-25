<?php

namespace App\Http\Controllers;


use App\Models\Balance;
use App\Models\Order;
use App\Models\OrderAction;
use App\Models\SadeghiTelegramOrder;
use App\Models\Service;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class OrderController extends Controller
{
    public function index()
    {
        $query = Order::query()
            ->select('orders.*')
            ->selectSub(
            // Single subquery with conditional counts instead of 4 separate withCount subqueries
            // This generates one correlated subquery instead of four
                \App\Models\OrderAction::selectRaw("
                    CONCAT(
                        COALESCE(SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END), 0), ',',
                        COALESCE(SUM(CASE WHEN status = 'free' THEN 1 ELSE 0 END), 0), ',',
                        COALESCE(SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END), 0), ',',
                        COALESCE(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END), 0)
                    )
                ")->whereColumn('order_actions.order_id', 'orders.id'),
                'action_counts_raw'
            )
            ->with('service:id,service');

        // Filter by Order ID
        if ($orderId = request('order_id')) {
            $query->where('orders.id', $orderId);
        }

        // Filter by Link
        if ($link = request('link')) {
            $query->where('target_link', 'like', '%' . $link . '%');
        }

        // Filter by Status
        if ($status = request('status')) {
            $query->where('status', $status);
        }

        // Filter by Service Type
        if ($serviceType = request('service_type')) {
            $query->where('service_type', $serviceType);
        }

        // Filter by Date Range
        if ($dateFrom = request('date_from')) {
            $query->whereDate('orders.created_at', '>=', $dateFrom);
        }
        if ($dateTo = request('date_to')) {
            $query->whereDate('orders.created_at', '<=', $dateTo);
        }

        $orders = $query->orderBy('orders.id', 'desc')->paginate(200);

        // Parse the concatenated counts into separate attributes for frontend compatibility
        // Frontend expects: sent_actions_count, free_actions_count, processing_actions_count, failed_actions_count
        $orders->getCollection()->transform(function ($order) {
            $counts = explode(',', $order->action_counts_raw ?? '0,0,0,0');
            $order->sent_actions_count = (int) ($counts[0] ?? 0);
            $order->free_actions_count = (int) ($counts[1] ?? 0);
            $order->processing_actions_count = (int) ($counts[2] ?? 0);
            $order->failed_actions_count = (int) ($counts[3] ?? 0);
            unset($order->action_counts_raw);
            return $order;
        });

        return $orders;
    }

    public function create()
    {
        return tryCatch(fn() => $this->placeCommentOrder(request('link'), 0), 'Order placed successfully');
    }

    public function delete()
    {
        return tryCatch(
            fn() => Order::query()->whereIn('id', request('ids'))->delete(),
            'Order(s) deleted successfully',
        );
    }

    public function finish()
    {
        return tryCatch(
            function () {
                $ids = request('ids', [request('id')]);
                $ids = array_filter($ids);
                $maxRetries = 3;

                foreach ($ids as $orderId) {
                    $attempt = 0;
                    while ($attempt < $maxRetries) {
                        try {
                            DB::transaction(function () use ($orderId) {
                                $order = Order::query()
                                    ->where('id', $orderId)
                                    ->lockForUpdate()
                                    ->first();

                                if (!$order) {
                                    throw new \Exception('Order not found');
                                }

                                // Calculate how many actions need to be completed
                                $remainingCount = $order->total_count - $order->completed_count;

                                if ($remainingCount > 0) {
                                    // Always deduct balance for remaining
                                    $this->deductBalance($order->service_type, $remainingCount);

                                    // Only update actions if is_prepared = 2 (actions exist)
                                    if ($order->is_prepared == 2) {
                                        $order->actions()
                                            ->whereNotIn('status', ['sent', 'failed'])
                                            ->update(['status' => 'sent']);
                                    }
                                }

                                $order->completed_count = $order->total_count;
                                $order->status = 'Completed';
                                $order->save();
                            });

                            break; // Success, move to next order

                        } catch (\Illuminate\Database\QueryException $e) {
                            $attempt++;
                            if ($attempt >= $maxRetries || !str_contains($e->getMessage(), 'deadlock')) {
                                throw $e;
                            }
                            usleep(100000 * $attempt);
                        }
                    }
                }
            },
            'Order(s) finished successfully',
        );
    }

    private function deductBalance($actionType, $count = 1)
    {
        $rates = [
            'comment' => 0.0003,
            'view_story' => 0.00005,
            'view_all_stories' => 0.00005,
            'save_post' => 0.00004,
        ];

        $rate = $rates[$actionType] ?? 0.00005;
        $totalCharge = $rate * $count;

        // Atomic decrement to prevent race conditions with concurrent balance updates
        Balance::where('customer', 'sadeghi')->decrement('balance', $totalCharge);
    }

    public function fail()
    {
        return tryCatch(
            function () {
                $ids = request('ids', [request('id')]);
                $ids = array_filter($ids);

                Order::query()->whereIn('id', $ids)->update([
                    'status' => 'Canceled',
                    'is_prepared' => 0,
                ]);
            },
            'Order(s) failed successfully',
        );
    }

    public function reset()
    {
        return tryCatch(
            function () {
                $ids = request('ids', [request('id')]);
                $ids = array_filter($ids);

                foreach ($ids as $orderId) {
                    $order = Order::query()->find($orderId);
                    if (!$order) continue;

                    $order->status = 'Pending';
                    $order->is_prepared = 0;
                    $order->completed_count = 0;
                    $order->action_data = null;
                    $order->save();

                    if ($order->service_type === 'comment') {
                        // For comments: keep actions but reset status and account
                        $order->actions()->update([
                            'status' => 'free',
                            'account_id' => null,
                        ]);
                    } else {
                        // For view_story and save_post: delete actions (preparer will recreate them)
                        $order->actions()->delete();
                    }
                }
            },
            'Order(s) reset successfully',
        );
    }

    public function changeProcessingToFree()
    {
        return tryCatch(
            function () {
                $ids = request('ids', [request('id')]);
                $ids = array_filter($ids);

                foreach ($ids as $orderId) {
                    $order = Order::query()->find($orderId);
                    if (!$order) continue;

                    // If order was canceled, refund the remaining balance first
                    if ($order->status === 'Canceled') {
                        $remaining = $order->total_count - $order->completed_count;
                        if ($remaining > 0) {
                            $this->refundBalance($order->service_type, $remaining);
                        }
                    }

                    // Send to prepare queue (works for all service types)
                    $order->status = 'Pending';
                    $order->is_prepared = 0;
                    $order->save();

                    // Reset all non-sent actions to free
                    $order->actions()->where('status', '!=', 'sent')->update([
                        'status' => 'free',
                        'account_id' => null
                    ]);
                }
            },
            'Order(s) processing actions reset successfully',
        );
    }

    private function refundBalance($actionType, $count)
    {
        $rates = [
            'comment' => 0.0003,
            'view_story' => 0.00005,
            'view_all_stories' => 0.00005,
            'save_post' => 0.00004,
        ];

        $rate = $rates[$actionType] ?? 0.00005;
        $totalRefund = $rate * $count;

        // Atomic increment to prevent race conditions with concurrent balance updates
        Balance::where('customer', 'sadeghi')->increment('balance', $totalRefund);
    }

    public function v3()
    {

        $action = request('action');

        $serviceMap = [
            740 => ['type' => 'comment', 'rate' => 0.30],
            741 => ['type' => 'view_story', 'rate' => 0.05],
            743 => ['type' => 'save_post', 'rate' => 0.04],
        ];

        if ($action === 'balance') {
            $balance = Balance::query()->where('customer', 'sadeghi')->first();
            return response()->json([
                'status' => 'success',
                'balance' => $balance->balance ?? 0,
                'currency' => 'IRT'
            ]);
        }

        if ($action === 'services') {
            return response()->json([
                [
                    "service" => 740,
                    "name" => "Comment",
                    "category" => "SSM-fire",
                    "rate" => "0.30$",
                    "min" => 5,
                    "max" => 4000,
                    "type" => "custom_comments",
                    "desc" => "Instagram Comment Service",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
                [
                    "service" => 741,
                    "name" => "View Story",
                    "category" => "SSM-fire",
                    "rate" => "0.05$",
                    "min" => 10,
                    "max" => 4000,
                    "type" => "default",
                    "desc" => "View first or specific story",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
                [
                    "service" => 743,
                    "name" => "Save Post",
                    "category" => "SSM-fire",
                    "rate" => "0.04$",
                    "min" => 10,
                    "max" => 4000,
                    "type" => "default",
                    "desc" => "Save a post or reel",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
            ]);
        }

        if ($action === 'add') {
            $serviceCode = (int) request('service');
            $link = request('link');
            $quantity = (int) request('quantity');

            if (!isset($serviceMap[$serviceCode])) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Invalid service'
                ]);
            }

            $serviceInfo = $serviceMap[$serviceCode];
            $serviceType = $serviceInfo['type'];

            if ($serviceType === 'comment') {
                return $this->placeCommentOrder($link, $quantity);
            }

            if ($serviceType === 'save_post') {
                if (!$this->isValidPostOrReelLink($link)) {
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Invalid link. Must be a post or reel URL.'
                    ]);
                }
            }

            $cleanLink = $this->cleanInstagramLink($link);

            // Duplicate link validation
            $duplicateCheck = $this->checkDuplicateLink($cleanLink, $serviceType);
            if ($duplicateCheck !== true) {
                return $duplicateCheck;
            }

            $minQty = ($serviceType === 'comment') ? 5 : 10;
            $maxQty = ($serviceType === 'comment') ? 2000 : 10000;

            if ($quantity < $minQty || $quantity > $maxQty) {
                return response()->json([
                    'status' => 'error',
                    'message' => "Quantity must be between {$minQty} and {$maxQty}"
                ]);
            }

            $service = Service::query()
                ->where('service', $serviceType)
                ->first();

            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => $serviceType,
                "target_link" => $cleanLink,
                "total_count" => $quantity,
                "status" => "Pending",
            ]);

            // view_story and save_post actions are created by OrderPreparer after data capture
            // No immediate action creation needed for these types

            return response()->json([
                'status' => 'success',
                'order' => $order->id
            ]);
        }

        if ($action === 'status') {
            return $this->getStatus($serviceMap);
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Invalid action'
        ]);
    }


    public function telegramGroupSender()
    {
        Log::info('telegramGroupSender', [
            'body' => r()->all(),
        ]);
        $action = request('action');
        if ($action === 'balance') {
            return response()->json([
                'status' => 'success',
                'balance' => 20,
                'currency' => 'IRT'
            ]);
        }

        if ($action === 'services') {
            return response()->json([
                [
                    "service" => 741,
                    "name" => "Link and quantity",
                    "category" => "SSM-fire",
                    "rate" => "1$",
                    "min" => 50,
                    "max" => "10M",
                    "type" => "like",
                    "desc" => "Best and Fast Comment",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                    "brand" => "",
                ]
            ]);
        }

        if ($action === 'add') {
            $commentsCount = r('quantity');
            $postLink = r('link');

            $order = SadeghiTelegramOrder::query()->create([
                "service_type" => 'like',
                "target_link" => $postLink,
                "total_count" => $commentsCount,
            ]);

            $botToken = "7217235633:AAH4TukyhmR2mb0HvPfG7BBSsXC4H0O2QcI";
            $chatId = "-1003317059009";
            $orderId = $order->id;
            $link = $postLink;
            $quantity = $commentsCount;

            $message = "#{$orderId}\n\n{$link}\n\n{$quantity}";

            $url = "https://api.telegram.org/bot{$botToken}/sendMessage";

            try {
                $response = Http::withoutVerifying()->post($url, [
                    'chat_id' => $chatId,
                    'text' => $message,
                    'disable_web_page_preview' => true,
                ]);

                $order->setStatusTo('Completed');

            } catch (\Exception $e) {
                Log::error('Something went wrong: ' . $e->getMessage());

                return response()->json([
                    'status' => 'error',
                    'message' => $e->getMessage()
                ], 500);
            }

            return response()->json([
                'status' => 'success',
                'order' => $order->id
            ]);
        }

        if ($action === 'status') {
            if ($orders = request('orders')) {
                $orderIds = explode(',', $orders);
                $response = [];

                foreach ($orderIds as $id) {
                    $id = trim($id);
                    $order = SadeghiTelegramOrder::query()->find($id);

                    if (!$order) {
                        $response[$id] = "Incorrect order ID";
                        continue;
                    }

                    $response[$id] = [
                        'order' => (string)$order->id,
                        'status' => $order->status,
                        'charge' => "0.0000",
                        'start_count' => $order->start_count,
                        'remains' => (string)$order->getRemains(),
                        'currency' => "USD"
                    ];
                }

                return response()->json($response);
            }
            if ($ordersInput = request('order')) {
                $order = Order::query()->find($ordersInput);

                if (!$order) {
                    return response()->json([
                        $ordersInput => "Incorrect order ID",
                        'status' => 'error',
                    ]);
                }

                return response()->json([
                    (string)$order->id => [
                        'order' => (string)$order->id,
                        'status' => $order->status ?? "Completed",
                        'charge' => "0.0000",
                        'start_count' => $order->start_count,
                        'remains' => (string)1,
                        'currency' => "USD"
                    ]
                ]);
            }
        }
    }


    public function getActions()
    {
        $order = Order::query()->find(r('orderId'));

        // If is_prepared != 2, no actions exist yet (for view_story and save_post)
        if (in_array($order->service_type, ['view_story', 'save_post']) && $order->is_prepared != 2) {
            return response()->json([
                'message' => 'Order is not prepared yet',
                'is_prepared' => $order->is_prepared,
                'actions' => []
            ]);
        }

        return $order->actions()
            ->with('account:id,username')
            ->orderBy('id')
            ->get();
    }


    public function v4()
    {
        $action = request('action');

        $serviceMap = [
            740 => ['type' => 'comment', 'rate' => 0.30],
            741 => ['type' => 'view_story', 'rate' => 0.05],
            742 => ['type' => 'view_all_stories', 'rate' => 0.05],
            743 => ['type' => 'save_post', 'rate' => 0.04],
        ];

        if ($action === 'balance') {
            $balance = Balance::query()->where('customer', 'sadeghi')->first();
            return response()->json([
                'status' => 'success',
                'balance' => $balance->balance ?? 0,
                'currency' => 'IRT'
            ]);
        }

        if ($action === 'services') {
            return response()->json([
                [
                    "service" => 740,
                    "name" => "Comment",
                    "category" => "SSM-fire",
                    "rate" => "0.25$",
                    "min" => 5,
                    "max" => 2000,
                    "type" => "custom_comments",
                    "desc" => "Instagram Comment Service",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
                [
                    "service" => 741,
                    "name" => "View Story",
                    "category" => "SSM-fire",
                    "rate" => "0.025$",
                    "min" => 10,
                    "max" => 10000,
                    "type" => "default",
                    "desc" => "View first or specific story",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
                [
                    "service" => 742,
                    "name" => "View All Stories",
                    "category" => "SSM-fire",
                    "rate" => "0.05$",
                    "min" => 10,
                    "max" => 10000,
                    "type" => "default",
                    "desc" => "View all stories of a user",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
                [
                    "service" => 743,
                    "name" => "Save Post",
                    "category" => "SSM-fire",
                    "rate" => "0.025$",
                    "min" => 10,
                    "max" => 10000,
                    "type" => "default",
                    "desc" => "Save a post or reel",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                ],
            ]);
        }

        if ($action === 'add') {
            $serviceCode = (int) request('service');
            $link = request('link');
            $quantity = (int) request('quantity');

            if (!isset($serviceMap[$serviceCode])) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Invalid service'
                ]);
            }

            $serviceInfo = $serviceMap[$serviceCode];
            $serviceType = $serviceInfo['type'];

            if ($serviceType === 'comment') {
                return $this->v4PlaceCommentOrder($link, $quantity);
            }

            if ($serviceType === 'save_post') {
                if (!$this->isValidPostOrReelLink($link)) {
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Invalid link. Must be a post or reel URL.'
                    ]);
                }
            }

            $cleanLink = $this->cleanInstagramLink($link);

            // Duplicate link validation
//            $duplicateCheck = $this->checkDuplicateLink($cleanLink, $serviceType);
//            if ($duplicateCheck !== true) {
//                return $duplicateCheck;
//            }

            $minQty = ($serviceType === 'comment') ? 5 : 1;
            $maxQty = ($serviceType === 'comment') ? 2000 : 10000;

            if ($quantity < $minQty || $quantity > $maxQty) {
                return response()->json([
                    'status' => 'error',
                    'message' => "Quantity must be between {$minQty} and {$maxQty}"
                ]);
            }

            $service = Service::query()
                ->where('service', $serviceType)
                ->first();

            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => $serviceType,
                "target_link" => $cleanLink,
                "total_count" => $quantity,
                "status" => "Pending",
            ]);

            // view_story and save_post actions are created by OrderPreparer after data capture
            // No immediate action creation needed for these types

            return response()->json([
                'status' => 'success',
                'order' => $order->id
            ]);
        }

        if ($action === 'status') {
            return $this->v4GetStatus($serviceMap);
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Invalid action'
        ]);
    }


    private function placeCommentOrder($link, $quantity)
    {
        $comments = request('comments');

        if (empty($comments)) {
            return response()->json([
                'status' => 'error',
                'message' => 'Comments are required for comment service'
            ]);
        }

        $commentList = explode("\n", $comments);
        $commentList = array_filter(array_map('trim', $commentList));

        if (count($commentList) === 0) {
            return response()->json([
                'status' => 'error',
                'message' => 'At least one comment is required'
            ]);
        }

        $cleanLink = $this->cleanInstagramLink($link);

        // Duplicate link validation
        $duplicateCheck = $this->checkDuplicateLink($cleanLink, 'comment');
        if ($duplicateCheck !== true) {
            return $duplicateCheck;
        }

        $service = Service::query()
            ->where('service', 'comment')
            ->first();

        // Wrap order + actions creation in a transaction to prevent race condition.
        // Without this, the Python preparer can see the order (is_prepared=0, status=Pending)
        // before the actions are inserted, causing "No comment action with content found" errors.
        $order = DB::transaction(function () use ($cleanLink, $commentList, $service) {
            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => 'comment',
                "target_link" => $cleanLink,
                "total_count" => count($commentList),
                "status" => "Pending",
            ]);

            foreach ($commentList as $comment) {
                OrderAction::query()->create([
                    'order_id' => $order->id,
                    'type' => 'comment',
                    'content' => $comment,
                    'status' => 'free',
                ]);
            }

            return $order;
        });

        return response()->json([
            'status' => 'success',
            'order' => $order->id
        ]);
    }

    private function getStatus($serviceMap)
    {
        if ($orders = request('orders')) {
            $orderIds = explode(',', $orders);
            $response = [];

            foreach ($orderIds as $id) {
                $id = trim($id);
                $order = Order::query()->find($id);

                if (!$order) {
                    $response[$id] = "Incorrect order ID";
                    continue;
                }

                $rate = $this->getRateForServiceType($order->service_type, $serviceMap);

                $response[$id] = [
                    'order' => (string) $order->id,
                    'status' => $order->status,
                    'charge' => $this->calculateCharge($order, $rate),
                    'start_count' => $order->start_count,
                    'remains' => (string) $order->getRemains(),
                    'currency' => "USD"
                ];
            }

            return response()->json($response);
        }

        if ($orderId = request('order')) {
            $order = Order::query()->find($orderId);

            if (!$order) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Incorrect order ID'
                ]);
            }

            $rate = $this->getRateForServiceType($order->service_type, $serviceMap);

            return response()->json([
                'status' => 'success',
                'order' => (string) $order->id,
                'order_status' => $order->status,
                'charge' => $this->calculateCharge($order, $rate),
                'start_count' => $order->start_count,
                'remains' => (string) $order->getRemains(),
                'currency' => "USD"
            ]);
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Order ID is required'
        ]);
    }

    private function calculateCharge($order, $rate)
    {
        $perUnitRate = $rate / 1000;
        return number_format($order->completed_count * $perUnitRate, 6);
    }

    private function v4PlaceCommentOrder($link, $quantity)
    {
        $comments = request('comments');

        if (empty($comments)) {
            return response()->json([
                'status' => 'error',
                'message' => 'Comments are required for comment service'
            ]);
        }

        $commentList = explode("\n", $comments);
        $commentList = array_filter(array_map('trim', $commentList));

        if (count($commentList) === 0) {
            return response()->json([
                'status' => 'error',
                'message' => 'At least one comment is required'
            ]);
        }

        $cleanLink = $this->cleanInstagramLink($link);

        // Duplicate link validation
        $duplicateCheck = $this->checkDuplicateLink($cleanLink, 'comment');
        if ($duplicateCheck !== true) {
            return $duplicateCheck;
        }

        $service = Service::query()
            ->where('service', 'comment')
            ->first();

        // Wrap order + actions creation in a transaction to prevent race condition.
        // Without this, the Python preparer can see the order (is_prepared=0, status=Pending)
        // before the actions are inserted, causing "No comment action with content found" errors.
        $order = DB::transaction(function () use ($cleanLink, $commentList, $service) {
            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => 'comment',
                "target_link" => $cleanLink,
                "total_count" => count($commentList),
                "status" => "Pending",
            ]);

            foreach ($commentList as $comment) {
                OrderAction::query()->create([
                    'order_id' => $order->id,
                    'type' => 'comment',
                    'content' => $comment,
                    'status' => 'free',
                ]);
            }

            return $order;
        });

        return response()->json([
            'status' => 'success',
            'order' => $order->id
        ]);
    }

    private function v4GetStatus($serviceMap)
    {
        if ($orders = request('orders')) {
            $orderIds = explode(',', $orders);
            $response = [];

            foreach ($orderIds as $id) {
                $id = trim($id);
                $order = Order::query()->find($id);

                if (!$order) {
                    $response[$id] = "Incorrect order ID";
                    continue;
                }

                $rate = $this->getRateForServiceType($order->service_type, $serviceMap);

                $response[$id] = [
                    'order' => (string) $order->id,
                    'status' => $order->status,
                    'charge' => $this->calculateChargeV4($order, $rate),
                    'start_count' => $order->start_count,
                    'remains' => (string) $order->getRemains(),
                    'currency' => "USD"
                ];
            }

            return response()->json($response);
        }

        if ($orderId = request('order')) {
            $order = Order::query()->find($orderId);

            if (!$order) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Incorrect order ID'
                ]);
            }

            $rate = $this->getRateForServiceType($order->service_type, $serviceMap);

            return response()->json([
                'status' => 'success',
                'order' => (string) $order->id,
                'order_status' => $order->status,
                'charge' => $this->calculateChargeV4($order, $rate),
                'start_count' => $order->start_count,
                'remains' => (string) $order->getRemains(),
                'currency' => "USD"
            ]);
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Order ID is required'
        ]);
    }

    private function calculateChargeV4($order, $rate)
    {
        $perUnitRate = $rate / 1000;
        return number_format($order->completed_count * $perUnitRate, 6);
    }

    /**
     * Check if link is duplicate based on service type
     * Only reject if order is still active (Pending or In progress)
     * Allow if previous order is Completed or Canceled
     */
    private function checkDuplicateLink($cleanLink, $serviceType)
    {
        $existingOrder = Order::query()
            ->where('target_link', $cleanLink)
            ->where('service_type', $serviceType)
            ->whereIn('status', ['Pending', 'In progress'])
            ->first();

        if (!$existingOrder) {
            return true;
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Duplicate link. An active order with this link already exists.'
        ]);
    }

    private function cleanInstagramLink($link)
    {
        $parsed = parse_url($link);

        $cleanUrl = '';

        if (isset($parsed['scheme'])) {
            $cleanUrl .= $parsed['scheme'] . '://';
        }

        if (isset($parsed['host'])) {
            $cleanUrl .= $parsed['host'];
        }

        if (isset($parsed['path'])) {
            $cleanUrl .= $parsed['path'];
        }

        return $cleanUrl;
    }

    private function isValidPostOrReelLink($link)
    {
        $patterns = [
            '/instagram\.com\/p\/[\w-]+/',
            '/instagram\.com\/reel\/[\w-]+/',
            '/instagram\.com\/[\w.]+\/reel\/[\w-]+/',
        ];

        foreach ($patterns as $pattern) {
            if (preg_match($pattern, $link)) {
                return true;
            }
        }

        return false;
    }

    private function getRateForServiceType($serviceType, $serviceMap)
    {
        foreach ($serviceMap
                 as $code => $info) {
            if ($info['type'] === $serviceType) {
                return $info['rate'];
            }
        }
        return 0.025;
    }
}
