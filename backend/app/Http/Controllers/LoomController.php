<?php

namespace App\Http\Controllers;

use App\Classes\LoomUploader;
use App\Models\Lead;
use App\Models\Loom;
use App\Models\Template;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class LoomController extends Controller
{

    public function index()
    {
        return Loom::query()
            ->select('id', 'original_name', 'path', 'state', 'description')
            ->with(['account:id,username', 'lead:id,username'])
            ->paginate(
                config('data.pagination.each_page.looms')
            );
    }

    public function delete()
    {
        try {
            DB::beginTransaction();
            $loomQuery = Loom::query()->whereIn('id', r('ids'));
            $looms = $loomQuery->get();
            $loomQuery->delete();

            $looms->each(
                fn(Loom $loom) => Storage::disk('public')->exists($loom->path) &&
                    Storage::disk('public')->delete($loom->path)
            );

            DB::commit();

            return jsonSuccess('Loom successfully deleted');

        } catch (\Exception $e) {
            DB::rollback();
            return jsonError($e->getMessage());
        }
    }

    public function view()
    {
        return Loom::query()
            ->select('id', 'original_name', 'path', 'state', 'description')
            ->with(['account:id,username', 'lead:id,username'])
            ->findOrFail(r('id'));
    }
}
