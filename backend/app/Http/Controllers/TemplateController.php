<?php

namespace App\Http\Controllers;

use App\Models\Account;
use App\Models\Color;
use App\Models\Template;
use \Carbon\Carbon;
use \Illuminate\Support\Facades\Storage;

class TemplateController extends Controller
{
    public function index()
    {

        $templates = Template::query()
            ->where('type', r('type'))
            ->with('category:id,title')
            ->with('tags:id,title')
            ->when(r('type') == 'carousel', function ($query) {
                $query->where('color_id', r('color'))
                    ->orderBy('color_id')
                    ->orderBy('uid');
            })->get();


        $data = match (r('type')) {
            'carousel', 'video-post' => $templates->groupBy('carousel_id'),
            default => $templates,
        };

        return [
            'data' => $data,
            'type' => r('type')
        ];
    }

    public function create()
    {

        r()->validate([
            'type' => 'required',
            'text' => [
                'required',
                'string',
                function ($attribute, $value, $fail) {
                    $uniqueCheck = Template::query()
                        ->where('type', r('type'))
                        ->where('text', $value)
                        ->exists();

                    if ($uniqueCheck) {
                        $fail('This ' . r('type') . ' has already been taken.');
                    }
                },
            ]
        ]);

        return tryCatch(
            fn() => r('bulk_insertion') ? Template::createBulk() : Template::createOne(),
            'Template created successfully',
        );
    }

    public function uploadFile()
    {
        $file = r()->file('file');
        $day = Carbon::now()->day;
        $month = Carbon::now()->month;
        $mediaType = r('mediaType');
        $theme = r('theme');
        $carouselId = r('carouselId');
        $colorId = null;

        $subType = match ($file->extension()) {
            'jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp',
            'tiff', 'heif', 'svg' => 'image',

            'webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv',
            'mp4', 'm4p', 'ogg', 'm4v', 'avi', 'wmv',
            'mov', 'qt', 'flv', 'swf', 'avchd' => 'video',

            default => abort(422, 'unhandled file extension')
        };

        if ($mediaType == 'video-post') {

            $query = Template::query()
                ->where('type', $mediaType)
                ->where('carousel_id', $carouselId)
                ->where('sub_type', $subType);

            if ($query->exists()) {
                Template::query()
                    ->where('type', $mediaType)
                    ->where('carousel_id', $carouselId)
                    ->get()
                    ->each(function ($template) {

                        $path = "public/{$template->text}";

                        Storage::exists($path) && Storage::delete($path);

                        $template->delete();
                    });

                return response()->json(['message' => "More than one $subType file uploaded"], 422);
            }
        }

//        if ($mediaType === 'carousel') {
//            $color = Color::whereTitle($theme)->first();
//
////            if (!$color) {
////                return response()->json(['message' => "The $theme not recorded in the database"], 422);
////            }
//
//            $colorId = $color?->id;
//        }

        if ($mediaType === 'avatar' && $subType === 'video') {
            return response()->json(['message' => 'unhandled file extension for avatar type'], 422);
        }

        if ($mediaType === 'carousel') {
            $path = "uploads/$mediaType/$theme/$carouselId";
        } elseif ($mediaType === 'video-post') {
            $path = "uploads/$mediaType/$carouselId";
        } else {
            $path = "uploads/$mediaType/$month/$day";
        }

        $filePath = $file->store($path, 'public');

        Template::query()->create([
            'text' => $filePath,
            'type' => $mediaType,
            'sub_type' => $subType,
            'carousel_id' => $carouselId,
            'uid' => $mediaType === 'carousel' ? r('uid') : null,
            'color_id' => $colorId,
            'category_id' => r('category'),
            'caption' => r('caption')
        ]);
    }

    public function delete()
    {
        return tryCatch(
            function () {
                $templates = Template::query();

                match (r('receivedType')) {
                    'carousel', 'video-post' => $templates->whereIn('carousel_id', r('ids')),
                    default => $templates->whereIn('id', r('ids'))
                };

                $templates->get()
                    ->each(function ($template) {
                        if (in_array($template->type, config('data.template.multimedia_type'))) {

                            $path = "public/{$template->text}";

                            Storage::exists($path) && Storage::delete($path);
                        }

                        $template->tags()->detach();
                        $template->delete();
                    });
            },
            'Template(s) deleted successfully',
        );
    }


    public function fetchTypes()
    {
        return Template::$types;
    }

    public function fetchColors()
    {
        return Color::get();
    }

    public function view()
    {
        return Template::query()
            ->select('id', 'category_id', 'caption')
            ->findOrFail(r('id'));
    }

    public function update()
    {
        return tryCatch(
            fn() => Template::query()->whereId(r('id'))->update(r()->except('id')),
            'Template updated successfully',
        );
    }

    public function getNameUsername()
    {
        $account = Account::query()->findOrFail(r('id'));
        $tagIds = $account->tags()->pluck('id')->toArray();

        return Template::query()
            ->where('type', 'name-username')
            ->whereHas('tags')//templates that have at least one tag
            ->whereDoesntHave('tags', fn($q) => $q->whereNotIn('tags.id', $tagIds))
            ->inRandomOrder()
            ->first();
    }
}
