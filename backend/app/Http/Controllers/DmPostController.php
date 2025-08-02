<?php

namespace App\Http\Controllers;

use App\Models\DmPost;
use Illuminate\Http\Request;

class DmPostController extends Controller
{
    public function index()
    {
        return DmPost::query()
            ->with('category')
            ->paginate(20);
    }

    public function getDmPosts()
    {
        return DmPost::query()->get();
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:dm_posts|max:1000',
        ]);

        return tryCatch(
            fn() => DmPost::create([
                'title' => r('title'),
                'priority' => r('priority')??0,
                'category_id' => r('category'),
            ]),
            'DM post created successfully'
        );
    }

    public function edit($id, Request $request)
    {
        $request->validate([
            'title' => 'required|unique:dm_posts,title,' . $id . '|max:1000',
        ]);

        return tryCatch(
            fn() => DmPost::where('id', $id)->update($request->only('title')),
            'DM post updated successfully'
        );
    }

    public function delete(Request $request)
    {
        return tryCatch(
            fn() => DmPost::whereIn('id', $request->input('ids'))->delete(),
            'DM post deleted successfully'
        );
    }

    public function search()
    {
        return DmPost::query()
            ->where('title', 'like', '%' . request('q') . '%')
            ->get();
    }
}
