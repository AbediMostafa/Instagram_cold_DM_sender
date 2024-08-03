<?php

namespace App\Http\Resources\account;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class AccountCollection extends ResourceCollection
{
//    public static $wrap = null;

    public function toArray(Request $request): array
    {
        return [
            $this->collection,
        ];
    }
}
