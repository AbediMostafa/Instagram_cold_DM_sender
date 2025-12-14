<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Account;
use App\Models\Order;
use App\Models\OrderComment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class OrderController extends Controller
{
    public function index()
    {
        return Order::query()->orderBy('id', 'desc')->paginate(75);

    }

    public function placeOrder()
    {
        $comments = explode("\n", request('comments'));

        $order = Order::query()->create([
            "customer" => r("site_url") || r('customer'),
            "service_type" => "like_and_comment",
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
            function () {
                $order = Order::query()->find(request('id'));
                $order->status = 'In progress';
                $order->save();

                $order->comments()->where('status', 'processing')->update([
                    'status' => 'free',
                    'account_id' => null
                ]);

            },
            'Order reseted successfully',
        );
    }


    public function v3()
    {
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
                    "service" => 740,
                    "name" => "Comment",
                    "category" => "SSM-fire",
                    "rate" => "1$",
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
}
