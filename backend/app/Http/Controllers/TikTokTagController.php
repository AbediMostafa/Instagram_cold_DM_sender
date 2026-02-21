<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\TikTokTag;
use Illuminate\Http\Request;

class TikTokTagController extends Controller
{
    public function index()
    {
        return tryCatch(
            fn() => TikTokTag::query()->create(r()->all()),
            'Tag created successfully'
        );
    }

    public function destroy($id)
    {
        return tryCatch(
            fn() => TikTokTag::query()->where('id', $id)->delete(),
            'Tag deleted successfully'
        );
    }
}
