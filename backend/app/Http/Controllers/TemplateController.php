<?php

namespace App\Http\Controllers;

use App\Models\Color;
use App\Models\Template;
use \Carbon\Carbon;
use \Illuminate\Support\Facades\Storage;

class TemplateController extends Controller
{
    public function index()
    {
        return Template::query()
            ->orderBy('type')
            ->paginate(
                config('data.pagination.each_page.templates')
            );
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
            fn() => Template::query()->create([
                'text' => r('text'),
                'type' => r('type'),
            ]),
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

        if ($mediaType === 'carousel') {
            $color = Color::whereTitle($theme)->first();

            if(!$color){
                abort(422, "The $theme not recorded in the database");
            }

            $colorId = $color?->id;
        }

        $extension = match ($file->extension()) {
            'jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp',
            'tiff', 'heif', 'svg' => 'image',

            'webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv',
            'mp4', 'm4p', 'ogg', 'm4v', 'avi', 'wmv',
            'mov', 'qt', 'flv', 'swf', 'avchd' => 'video',

            default => abort(422, 'unhandled file extension')
        };

        if ($mediaType === 'avatar' && $extension === 'video') {
            abort(422, 'unhandled file extension for avatar type');
        }

        $path = $mediaType === 'carousel' ?
            "uploads/$mediaType/$theme/$carouselId" :
            "uploads/$mediaType/$month/$day";

        $filePath = $file->store($path, 'public');

        Template::query()->create([
            'text' => $filePath,
            'type' => $mediaType,
            'carousel_id' => $mediaType === 'carousel' ? $carouselId : null,
            'uid' => $mediaType === 'carousel' ? r('uid') : null,
            'color_id' => $colorId,
            'caption' => r('caption')
        ]);
    }


    public function delete()
    {
        return tryCatch(
            fn() => Template::query()
                ->whereIn('id', r('ids'))
                ->get()
                ->each(function ($template) {
                    if (in_array($template->type, config('data.template.multimedia_type'))) {

                        $path = "public/{$template->text}";

                        Storage::exists($path) && Storage::delete($path);
                    }

                    $template->delete();

                }),
            'Template(s) deleted successfully',
        );
    }
}
