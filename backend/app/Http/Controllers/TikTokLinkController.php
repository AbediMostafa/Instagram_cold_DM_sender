<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\TikTokLink;
use Illuminate\Http\Request;

class TikTokLinkController extends Controller
{
    public function index()
    {
        return response()->json(
            TikTokLink:: query()
                ->when(
                    r('search'),
                    function ($_) {
                        $_->where(r('type'), likeOperator(), '%' . r('search') . '%');
                    }
                )
                ->orderByDesc('updated_at')
                ->paginate(20)
        );
    }

    public function store()
    {
//        return r()->all();
        TikTokLink::query()->insert(r('posts'));

        return response()->json(['success' => true]);
    }

    public function destroy($id)
    {
        TikTokLink::where('id', $id)->delete();
        return response()->json(['success' => true]);
    }

    public function update($id)
    {
        // Find the record
        $tiktokLink = TikTokLink::findOrFail($id);

        $data = r()->input('form');

        // Optional: validate
        $validated = validator($data, [
            'name' => 'required|string|max:255',
            'offer' => 'nullable|string|max:255',
            'spark_id' => 'nullable|string|max:255',
            'geo' => 'nullable|string|max:255',
            'post_link' => 'required|url|max:500',
        ])->validate();

        // Update the record
        $tiktokLink->update($validated);

        // Return JSON response
        return response()->json([
            'message' => 'TikTok post updated successfully.',
            'data' => $tiktokLink
        ]);
    }
}
