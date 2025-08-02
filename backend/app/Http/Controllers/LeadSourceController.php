<?php

namespace App\Http\Controllers;

use App\Models\LeadSource;
use Illuminate\Http\Request;

class LeadSourceController extends Controller
{
    public function index()
    {
        return LeadSource::query()
            ->with('category')
            ->paginate(20);
    }

    public function getLeadSources()
    {
        return LeadSource::query()->get();
    }

    public function create(Request $request)
    {
        $request->validate([
            'title' => 'required|unique:lead_sources|max:255',
        ]);

        return tryCatch(
            fn() => LeadSource::create([
                'title' => r('title'),
                'category_id' => r('category'),
            ]),
            'Lead source created successfully'
        );
    }

    public function edit($id, Request $request)
    {
        $request->validate([
            'title' => 'required|unique:lead_sources,title,' . $id . '|max:255',
        ]);

        return tryCatch(
            fn() => LeadSource::where('id', $id)->update($request->only('title')),
            'Lead source updated successfully'
        );
    }

    public function delete(Request $request)
    {
        return tryCatch(
            fn() => LeadSource::whereIn('id', $request->input('ids'))->delete(),
            'Lead source deleted successfully'
        );
    }

    public function search()
    {
        return LeadSource::query()
            ->where('title', 'like', '%' . request('q') . '%')
            ->get();
    }
}
