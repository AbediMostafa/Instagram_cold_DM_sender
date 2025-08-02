<?php

namespace App\Http\Controllers;

use App\Models\Hashtag;
use Illuminate\Http\Request;

class HashtagController extends Controller
{
    public function index()
    {
        return Hashtag::query()
            ->with('category')
            ->paginate(20);
    }

    public function getHashtags()
    {
        return Hashtag::query()->get();
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:hashtags|max:255',
        ]);

        return tryCatch(
            fn() => Hashtag::create([
                'title'=>r('title'),
                'category_id'=>r('category'),
                ]),
            'Hashtag created successfully'
        );
    }

    public function edit($id, Request $request)
    {
        $request->validate([
            'title' => 'required|unique:hashtags,title,' . $id . '|max:255',
        ]);

        return tryCatch(
            fn() => Hashtag::where('id', $id)->update($request->only('title')),
            'Hashtag updated successfully'
        );
    }

    public function delete(Request $request)
    {
        return tryCatch(
            fn() => Hashtag::whereIn('id', $request->input('ids'))->delete(),
            'Hashtag deleted successfully'
        );
    }

    public function search()
    {
        return Hashtag::query()
            ->where('title', 'like', '%' . request('q') . '%')
            ->get();
    }
}
