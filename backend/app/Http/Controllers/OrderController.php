<?php

namespace App\Http\Controllers;


use App\Http\Controllers\Controller;
use App\Models\Account;
use App\Models\Balance;
use App\Models\Order;
use App\Models\OrderAction;
use App\Models\OrderComment;
use App\Models\SadeghiTelegramOrder;
use App\Models\Service;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class OrderController extends Controller
{
    public function index()
    {
        return Order::query()
            ->with('service:id,service')
            ->orderBy('id', 'desc')->paginate(75);

    }


    // public function placeOrder()
    // {
    //     $comments = explode("\n", request('comments'));
    //     $service = Service::query()
    //         ->where('service', "like_and_comment")
    //         ->first();
    //
    //     $order = Order::query()->create([
    //         "customer" => r("site_url") || r('customer'),
    //         "service_id" => $service->id,
    //         "target_link" => r("link"),
    //         "total_count" => count($comments),
    //     ]);
    //
    //     foreach ($comments as $comment) {
    //         OrderComment::query()->create([
    //             'order_id' => $order->id, 'content' => $comment
    //         ]);
    //     }
    //
    //     return $order;
    // }

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
                $order = Order::query()->find(request('id'));
                $order->completed_count = $order->total_count;
                $order->status = 'Completed';
                $order->save();
            },
            'Order finished successfully',
        );
    }

    public function fail()
    {

        return tryCatch(
            function () {
                $order = Order::query()->find(request('id'));
                $order->status = 'Canceled';
                $order->save();
            },
            'Order failed successfully',
        );
    }

    public function reset()
    {

        return tryCatch(
            function () {
                $order = Order::query()->find(request('id'));
                $order->status = 'Pending';
                $order->completed_count = 0;
                $order->save();

                $order->actions()->update([
                    'status' => 'free',
                    'account_id' => null
                ]);

            },
            'Order reset successfully',
        );
    }

    public function changProcessingCommentsToFree()
    {
        return tryCatch(
            fn() => Order::query()
                ->find(r('id'))
                ->changeProcessingToFree(),
            'Order reseted successfully',
        );
    }


    public function v3()
    {
        $action = request('action');

        $serviceMap = [
            740 => ['type' => 'comment', 'rate' => 0.25],
            741 => ['type' => 'view_story', 'rate' => 0.025],
            742 => ['type' => 'view_all_stories', 'rate' => 0.05],
            743 => ['type' => 'save_post', 'rate' => 0.025],
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

            // Clean the link - remove tracking parameters
            $cleanLink = $this->cleanInstagramLink($link);

            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => $serviceType,
                "target_link" => $cleanLink,
                "total_count" => $quantity,
                "completed_count" => 0,
                "status" => "Pending",
            ]);

            for ($i = 0; $i < $quantity; $i++) {
                OrderAction::query()->create([
                    'order_id' => $order->id,
                    'type' => $serviceType,
                    'status' => 'free',
                ]);
            }

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


    // public function v3_old()
    // {
    //     $action = request('action');
    //
    //     if ($action === 'balance') {
    //         $balance = Balance::query()->where('customer', 'sadeghi')->first();
    //         return response()->json([
    //             'status' => 'success',
    //             'balance' => $balance->balance,
    //             'currency' => 'IRT'
    //         ]);
    //     }
    //
    //     if ($action === 'services') {
    //         return response()->json([
    //             [
    //                 "service" => 740,
    //                 "name" => "Comment",
    //                 "category" => "SSM-fire",
    //                 "rate" => "0.25$",
    //                 "min" => 5,
    //                 "max" => 2000,
    //                 "type" => "custom_comments",
    //                 "desc" => "Best and Fast Comment",
    //                 "dripfeed" => false,
    //                 "refill" => false,
    //                 "cancel" => false,
    //                 "brand" => "",
    //             ]
    //         ]);
    //     }
    //
    //     if ($action === 'add') {
    //         $order = $this->placeOrder();
    //         return response()->json([
    //             'status' => 'success',
    //             'order' => $order->id
    //         ]);
    //     }
    //
    //     if ($action === 'status') {
    //         if ($orders = request('orders')) {
    //             $orderIds = explode(',', $orders);
    //             $response = [];
    //
    //             foreach ($orderIds as $id) {
    //                 $id = trim($id);
    //                 $order = Order::query()->find($id);
    //
    //                 if (!$order) {
    //                     $response[$id] = "Incorrect order ID";
    //                     continue;
    //                 }
    //
    //                 $response[$id] = [
    //                     'order' => (string)$order->id,
    //                     'status' => $order->status,
    //                     'charge' => "0.0000",
    //                     'start_count' => $order->start_count,
    //                     'remains' => (string)$order->getRemains(),
    //                     'currency' => "USD"
    //                 ];
    //             }
    //
    //             return response()->json($response);
    //         }
    //         if ($ordersInput = request('order')) {
    //             $order = Order::query()->find($ordersInput);
    //
    //             if (!$order) {
    //                 return response()->json([
    //                     $ordersInput => "Incorrect order ID",
    //                     'status' => 'error',
    //                 ]);
    //             }
    //
    //             return response()->json([
    //                 (string)$order->id => [
    //                     'order' => (string)$order->id,
    //                     'status' => $order->status ?? "Completed",
    //                     'charge' => "0.0000",
    //                     'start_count' => $order->start_count,
    //                     'remains' => (string)$order->getRemains(),
    //                     'currency' => "USD"
    //                 ]
    //             ]);
    //         }
    //     }
    // }

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


    public function getComment()
    {
        return Order::query()->find(r('orderId'))
            ->actions()
            ->orderBy('id')
            ->get();

    }


    public function v4()
    {
        $action = request('action');

        $serviceMap = [
            740 => ['type' => 'comment', 'rate' => 0.25],
            741 => ['type' => 'view_story', 'rate' => 0.025],
            742 => ['type' => 'view_all_stories', 'rate' => 0.05],
            743 => ['type' => 'save_post', 'rate' => 0.025],
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

            $cleanLink = $this->cleanInstagramLink($link);

            $order = Order::query()->create([
                "customer" => request("site_url") ?? request('customer'),
                "service_id" => $service ? $service->id : null,
                "service_type" => $serviceType,
                "target_link" => $cleanLink,
                "total_count" => $quantity,
                "completed_count" => 0,
                "status" => "Pending",
            ]);

            for ($i = 0; $i < $quantity; $i++) {
                OrderAction::query()->create([
                    'order_id' => $order->id,
                    'type' => $serviceType,
                    'status' => 'free',
                ]);
            }

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

        $service = Service::query()
            ->where('service', 'comment')
            ->first();

        $cleanLink = $this->cleanInstagramLink($link);

        $order = Order::query()->create([
            "customer" => request("site_url") ?? request('customer'),
            "service_id" => $service ? $service->id : null,
            "service_type" => 'comment',
            "target_link" => $cleanLink,
            "total_count" => count($commentList),
            "completed_count" => 0,
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
        return number_format($order->completed_count * $rate, 6);
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

        $service = Service::query()
            ->where('service', 'comment')
            ->first();

        $cleanLink = $this->cleanInstagramLink($link);

        $order = Order::query()->create([
            "customer" => request("site_url") ?? request('customer'),
            "service_id" => $service ? $service->id : null,
            "service_type" => 'comment',
            "target_link" => $cleanLink,
            "total_count" => count($commentList),
            "completed_count" => 0,
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
        return number_format($order->completed_count * $rate, 6);
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
        foreach ($serviceMap as $code => $info) {
            if ($info['type'] === $serviceType) {
                return $info['rate'];
            }
        }
        return 0.025;
    }
}
