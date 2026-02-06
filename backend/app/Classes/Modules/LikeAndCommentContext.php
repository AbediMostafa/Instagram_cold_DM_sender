<?php

namespace App\Classes\Modules;

use App\Models\Account;
use App\Models\Order;
use App\Models\OrderComment;
use App\Models\Profile;
use App\Models\Proxy;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

class LikeAndCommentContext
{
    public Account $account;
    public array $payload = [
        'orders' => [],
    ];

    public function __construct($account)
    {
        $this->account = $account;
    }

    public function handle()
    {
        $this->getOrder();
    }

    public function getOrder()
    {
        $orders = Order::getOrdersToExecute($this->account, 2);

        if ($orders->isEmpty()) {
            return $this->account->addCli('There is no order for this account');
        }

        foreach ($orders as $order) {
            $this->account->addCli("Processing order :{$order->id}");

            $comment = OrderComment::getCommentToExecute($order->id);

            if (!$comment) {
                $this->account->addCli("No free comment for order {$order->id}");
                continue;
            }

            $this->account->addCli("Selected comment {$comment->content}");

            $comment->status = 'pending';
            $comment->account_id = $this->account->id;
            $comment->save();

            $this->payload['orders'][$order->id] = [
                'id' => $order->id,
                'target_link' => $order->target_link,
                'comment' => [
                    'id' => $comment->id,
                    'content' => $comment->content,
                ]
            ];
        }
    }
}
