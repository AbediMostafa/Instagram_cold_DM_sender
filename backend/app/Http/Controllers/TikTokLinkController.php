<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\TikTokLink;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Process\Process;

class TikTokLinkController extends Controller
{
    public function index()
    {
        $allowedSorts = [
            'name',
            'offer',
            'spark_id',
            'geo',
            'comments',
            'likes',
            'shares',
            'saves',
            'play_counts',
            'updated_at'
        ];

        $sortBy = request('sort_by', 'updated_at');
        $sortDirection = request('sort_direction', 'desc');

        // جلوگیری از SQL Injection
        if (!in_array($sortBy, $allowedSorts)) {
            $sortBy = 'updated_at';
        }

        if (!in_array($sortDirection, ['asc', 'desc'])) {
            $sortDirection = 'desc';
        }

        $links = TikTokLink::query()
            ->when(
                request('search'),
                function ($query) {
                    $query->where(
                        request('type'),
                        likeOperator(),
                        '%' . request('search') . '%'
                    );
                }
            )
            ->when(
                $sortBy === 'name',
                function ($query) use ($sortDirection) {
                    $query->orderByRaw("
                    substring(name FROM '^[A-Za-z]+') $sortDirection,
                    CAST(substring(name FROM '[0-9]+$') AS INTEGER) $sortDirection
                ");
                },
                function ($query) use ($sortBy, $sortDirection) {
                    $query->orderBy($sortBy, $sortDirection);
                }
            )
            ->with('tags')
            ->orderBy($sortBy, $sortDirection)
            ->get();

        $links->transform(function ($link) {

            $folder = "tiktok/{$link->id}";

            if (Storage::disk('public')->exists($folder)) {

                $files = Storage::disk('public')->files($folder);

                $link->images = collect($files)
                    ->map(fn($file) => asset('storage/' . $file))
                    ->values();
            } else {
                $link->images = [];
            }

            return $link;
        });

        return response()->json($links);

//        $images = collect(json_decode($link->images))
//            ->map(fn($img) => asset('storage/'.$img));
//
//        return
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

    public function downloadImages()
    {
        $tikTokLink = TikTokLink::query()->find(r('id'));
        $folderPath = storage_path("app\\public\\tiktok\\{$tikTokLink->id}");

        $path = base_path("../script/generate_tiktok_images.py");

        $process = new Process([
            'python',
            $path,
            '--folder',
            $folderPath
        ]);

        $process->setTimeout(400);
        $process->run();

        $folderPath = storage_path("app\\public\\tiktok\\{$tikTokLink->id}\\output.zip");

        if (!file_exists($folderPath)) {
            return response()->json(['error' => 'Images not generated'], 400);
        }

        return response()->download($folderPath)->deleteFileAfterSend();
    }

    public function forceRun()
    {
        return tryCatch(function () {
            $path = base_path("../script/download_and_save_avatart.py");

            $process = new Process([
                'python',
                $path,
            ]);

            $process->setTimeout(400);
            $process->run();
        },
            'Script ran successfully'
        );
    }
}
