<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Account;
use App\Models\Balance;
use App\Models\Order;
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

    public function placeOrder()
    {
        $comments = explode("\n", request('comments'));
        $service = Service::query()
            ->where('service', "like_and_comment")
            ->first();

        $order = Order::query()->create([
            "customer" => r("site_url") || r('customer'),
            "service_id" => $service->id,
            "target_link" => r("link"),
            "total_count" => count($comments),
        ]);

        foreach ($comments as $comment) {
            OrderComment::query()->create([
                'order_id' => $order->id, 'content' => $comment
            ]);
        }

        return $order;
    }

    public function create()

    {
        return tryCatch(fn() => $this->placeOrder(), 'Order placed successfully');
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

                $order->comments()->update([
                    'status' => 'free',
                    'account_id' => null
                ]);

            },
            'Order failed successfully',
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
//        Log::info('V3 Incoming Request', [
//            'body'    => r()->all(),
//        ]);

        $action = request('action'); // or request()->input('action')

        if ($action === 'balance') {
            $balance = Balance::query()->where('customer', 'sadeghi')->first();
            return response()->json([
                'status' => 'success',
                'balance' => $balance->balance,
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
                    "desc" => "Best and Fast Comment",
                    "dripfeed" => false,
                    "refill" => false,
                    "cancel" => false,
                    "brand" => "",
                ]
            ]);
        }

        if ($action === 'add') {

            $order = $this->placeOrder();

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
                    $order = Order::query()->find($id);

                    if (!$order) {
                        $response[$id] = "Incorrect order ID";
                        continue;
                    }

                    $response[$id] = [
                        'order' => (string)$order->id,
                        'status' => $order->status,
                        'charge' => "0.0000", // or your own charge logic
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
                        'remains' => (string)$order->getRemains(),
                        'currency' => "USD"
                    ]
                ]);
            }
        }
    }

    public function telegramGroupSender()
    {

        Log::info('telegramGroupSender', [
            'body' => r()->all(),
        ]);
        $action = request('action'); // or request()->input('action')
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

            // Format the message exactly as you want
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
                // Handle any exception
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
            ->comments()
            ->orderBy('id')
            ->get();

    }
}
