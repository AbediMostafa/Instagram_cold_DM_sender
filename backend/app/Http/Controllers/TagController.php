<?php

namespace App\Http\Controllers;

use App\Models\Category;
use App\Models\Tag;
use App\Models\TikTokLink;
use App\Models\TikTokTag;
use Illuminate\Http\Request;

class TagController extends Controller
{

    public function index()
    {
        return Tag::query()->paginate(15);
    }

    public function tikTokTags()
    {
        return TikTokTag::query()->get();
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:tags|max:255',
        ]);

        return tryCatch(
            fn() => Tag::create($request->only('title')),
            'Tag created successfully'
        );
    }

    public function edit($id, Request $request)
    {
        $request->validate([
            'title' => 'required|unique:tags,title,' . $id . '|max:255',
        ]);

        return tryCatch(
            fn() => Tag::where('id', $id)->update($request->only('title')),
            'Tag updated successfully'
        );
    }

    public function delete(Request $request)
    {
        return tryCatch(
            fn() => Tag::whereIn('id', $request->input('ids'))->delete(),
            'Category deleted successfully'
        );
    }

    public function search()
    {
        return Tag::query()
            ->where('title', 'like', '%' . request('q') . '%')
            ->get();
    }
}
