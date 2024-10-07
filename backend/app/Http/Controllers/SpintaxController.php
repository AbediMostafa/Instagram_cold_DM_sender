<?php

namespace App\Http\Controllers;

use App\Models\Spintax;
use Illuminate\Http\Request;

class SpintaxController extends Controller
{

    public function index()
    {
        return Spintax::query()
            ->select('id', 'name', 'type', 'text', 'category_id')
            ->with(['category:id,title'])
            ->orderBy('type')
            ->paginate(
                config('data.pagination.each_page.spintaxes')
            );
    }

    public function view()
    {
        return Spintax::query()
            ->select('id', 'name', 'type', 'is_active', 'text')
            ->find(r('id'));
    }

    public function create()
    {
        r()->validate(
            [
                'name' => 'unique:spintaxes,name',
                'type' => [
                    'required',
                    fn($attribute, $value, $fail) =>
                        Spintax::where('type', $value)->where('category_id', r('category_id'))->exists() &&
                        $fail('A spintax with this type and category already exists.'),
                ],

            ],
            ['name.unique' => 'The name must be unique. This name is already taken.']
        );

        return tryCatch(
            fn() => Spintax::query()->create(r()->all())
            , 'Spintax created successfully'
        );
    }
}
