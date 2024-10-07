<?php

namespace App\Http\Controllers;

use App\Models\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function index()
    {
        return Category::all();
    }

    public function view()
    {
        return Category::findOrFail(r('categoryId'));
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:categories|max:255',
            'description' => 'nullable|string',
        ]);

        return tryCatch(
            fn() => Category::create($request->only('title', 'description')),
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
            fn() => Category::where('id', $id)->update($request->only('title', 'description')),
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
