<?php

namespace App\Http\Controllers;

use App\Models\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function index()
    {
        return Category::query()->paginate(5);
    }

    public function getCategories()
    {
        return Category::query()->select('id', 'title')->get();
    }

    public function view()
    {
        return Category::findOrFail(r('categoryId'));
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:categories|max:255',
            'number_of_follow_ups' => 'required',
            'hour_interval' => 'required',
            'description' => 'nullable|string',
        ]);

        return tryCatch(
            fn() => Category::create(
                $request->only('title', 'description', 'number_of_follow_ups','hour_interval')
            ),
            'Category created successfully'
        );
    }

    public function edit($id, Request $request)
    {
        $request->validate([
            'title' => 'required|unique:categories,title,' . $id . '|max:255',
            'description' => 'nullable|string',
        ]);

        return tryCatch(
            fn() => Category::where('id', $id)->update(
                $request->only('title', 'description', 'number_of_follow_ups','hour_interval')
            ),
            'Category updated successfully'
        );
    }

    public function delete(Request $request)
    {
        return tryCatch(
            fn() => Category::whereIn('id', $request->input('ids'))->delete(),
            'Category deleted successfully'
        );
    }
}
