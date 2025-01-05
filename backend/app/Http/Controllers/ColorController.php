<?php

namespace App\Http\Controllers;

use App\Models\Color;
use Illuminate\Http\Request;

class ColorController extends Controller
{
    /**
     * Get all colors
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        $colors = Color::all();
        return response()->json($colors);
    }

    /**
     * Store a new color
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255|unique:colors',
            'is_used' => 'boolean'
        ]);

        $color = Color::create($validated);
        return response()->json($color, 201);
    }

    /**
     * Update a color
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function update(Request $request, $id)
    {
        $color = Color::findOrFail($id);

        $validated = $request->validate([
            'title' => 'required|string|max:255|unique:colors,title,' . $id,
            'is_used' => 'boolean'
        ]);

        $color->update($validated);
        return response()->json($color);
    }

    /**
     * Delete a color
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function destroy($id)
    {
        $color = Color::findOrFail($id);
        $color->delete();
        return response()->json(null, 204);
    }
}
