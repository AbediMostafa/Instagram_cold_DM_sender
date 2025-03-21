<?php

namespace App\Http\Controllers;

use App\Models\Account;
use App\Models\Spintax;
use Illuminate\Http\Request;

class SpintaxController extends Controller
{

    public function index()
    {
        return Spintax::query()
            ->select('id', 'name', 'times', 'text', 'category_id')
            ->with(['category:id,title,number_of_follow_ups'])
            ->orderBy('category_id')
            ->orderBy('times')
            ->paginate(
                config('data.pagination.each_page.spintaxes')
            );
    }

    public function view()
    {
        return Spintax::query()
            ->select('id', 'name', 'times', 'text', 'category_id')
            ->with(['category:id,title,number_of_follow_ups'])
            ->find(r('id'));
    }

    public function create()
    {
        r()->validate(
            [
                'name' => 'unique:spintaxes,name',
                'times' => [
                    'required',
                    fn($attribute, $value, $fail) => Spintax::where('times', $value)->where('category_id', r('category_id'))->exists() &&
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

    public function update()
    {
        r()->validate([
            'data.name' => 'required',
            'data.text' => 'required',
            'data.times' => 'required',
        ]);

        return tryCatch(
            fn() => Spintax::query()
                ->where('id', r('data.id'))
                ->update([
                    'category_id' => r('data.category_id'),
                    'name' => r('data.name'),
                    'text' => r('data.text'),
                    'times' => r('data.times'),
                ]),
            'Spintax updated successfully'
        );
    }

    public function delete()
    {
        return tryCatch(
            fn() => Spintax::query()->whereIn('id', r('ids'))->delete(),
            'Spintax deleted successfully'
        );
    }
}
