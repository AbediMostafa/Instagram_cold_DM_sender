<?php

namespace App\Http\Controllers;

use App\Models\Lead;
use App\Services\ChangeLeadStateService;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use League\Csv\Reader;
use League\Csv\Writer;
use Nette\Schema\ValidationException;
use PHPUnit\Exception;

class LeadController extends Controller
{
    public function index()
    {
        return Lead::query()
            ->with([
                'account:id,username',
                'category:id,title',
                'tags:id,title',
                'user:id,name,email',
            ])
            ->when(
                r('queryParams.username'),
                fn($_) => $_->where('username', 'ilike', '%' . r('queryParams.username') . '%')
            )
            ->when(
                r('queryParams.tags'),
                fn($_) => $_->whereHas('tags', fn($_) => $_->whereIn('id', r('queryParams.tags')))
            )
            ->when(
                r('queryParams.category'),
                fn($_) => $_->where('category_id', r('queryParams.category'))
            )
            ->when(
                r('queryParams.statuses'),
                fn($_) => $_->whereIn('last_state', r('queryParams.statuses'))
            )
            ->when(
                r('queryParams.users'),
                fn($_) => $_->whereIn('user_id', r('queryParams.users'))
            )
            ->orderByDesc('id')
            ->paginate(
                config('data.pagination.each_page.leads')
            );
    }


    public function view()
    {
        return Lead::query()->with('account:id,username')->find(r('id'));
    }


    public function delete()
    {
        return tryCatch(
            fn() => Lead::query()
                ->whereIn('id', r('ids'))
                ->delete(),
            'Lead(s) deleted successfully',
        );
    }

    public function edit()
    {
        r()->validate([
            'username' => 'required|unique:leads,username,' . r('id')
        ]);

        return tryCatch(
            fn() => Lead::query()
                ->where('id', r('id'))
                ->update([
                    'username' => r('username'),
                ]),
            'Lead updated successfully',
        );
    }

    public function changeState()
    {
        return tryCatch(
            fn() => ChangeLeadStateService::makeInstance(r('ids'), r('state'))
                ->execute(),
            "Lead's state changed successfully",
            "Problem changing lead's state"
        );
    }

    public function setCategory()
    {
        return tryCatch(
            fn() => Lead::query()
                ->whereIn('id', r('leadIds'))
                ->update([
                    'category_id' => r('categoryId'),
                ]),
            'Lead(s) updated successfully',
            'Problem updating lead(s)',
        );
    }

    public function import()
    {
        r()->validate([
            'file' => 'required|file|mimes:csv,txt',
        ]);

        try {
            $file = r()->file('file');
            $csv = Reader::createFromPath($file->getPathname(), 'r');

            foreach ($csv as $row) {

                $lead = Lead::query()->firstOrCreate(
                    ['username' => $row[0]] // Attributes to check for an existing record
                );

                if (!empty(r('tags'))) {
                    $tags = json_decode(r('tags'));
                    $lead->tags()->attach($tags); // Attach the tags to the lead
                }
            }

            return response()->json(['message' => 'Leads imported successfully']);

        } catch (\Exception $e) {
            return $e->getMessage();
        }
    }

    public function getStatuses()
    {
        return Lead::$states;
    }

    public function export()
    {
        r()->validate([
            'numberOfLeads' => 'required|integer|min:1',
        ]);

        try {

            DB::beginTransaction();
            // Fetch the required number of leads that haven't been assigned a category yet
            $leads = Lead::whereNull('user_id')
                ->where('last_state', 'free')
                ->when(
                    r('tags'),
                    fn($_) => $_->whereHas('tags', fn($_) => $_->whereIn('id', r('tags')))
                )
                ->inRandomOrder() // Fetch random leads
                ->limit(r()->numberOfLeads)
                ->get();

            abort_if($leads->isEmpty(), 422, 'No leads available for export');

            // Mark the leads with the selected category and assign them to the logged-in user
            foreach ($leads as $lead) {
                $lead->update([
                    'category_id' => r()->categoryId,
                    'user_id' => Auth::id(),
                    'export_date' => now(),
                ]);

                $lead->histories()->create([
                    'user_id' => Auth::id()
                ]);
            }
            // Create CSV for download
            $csv = Writer::createFromString('');

            // Insert the headers
            $csv->insertOne(['ID', 'Username', 'Export Date', 'Category']);

            // Insert the lead data
            foreach ($leads as $lead) {
                $csv->insertOne([
                    $lead->id,
                    $lead->username,
                    $lead->export_date->format('Y-m-d H:i:s'), // Format date properly
                    $lead->category->title ?? 'N/A', // Ensure no empty values
                ]);
            }

            DB::commit();

            // Return CSV as download
            return response()->streamDownload(function () use ($csv) {
                echo $csv->toString();
            }, 'leads.csv', [
                'Content-Type' => 'text/csv',
                'Content-Disposition' => 'attachment; filename="leads.csv"',
            ]);

        } catch (\Exception $e) {
            DB::rollBack();

            return jsonError($e->getMessage());
        }
    }

    public function exportApi()
    {
        r()->validate([
            'username' => 'required',
            'password' => 'required',
            'number_of_leads' => 'required|integer|min:1',
            'category_id' => 'nullable|integer|exists:categories,id',
        ]);

        $credentials = [
            'email' => r('username'),
            'password' => r('password'),
        ];

        if (!Auth::attempt($credentials)) {
            return response()->json(['message' => 'Invalid credentials'], 422);
        }

        try {

            DB::beginTransaction();

            $leads = Lead::whereNull('user_id')
                ->select('id', 'username')
                ->where('last_state', 'free')
                ->inRandomOrder()
                ->limit(r('number_of_leads'))
                ->get();

            if ($leads->isEmpty()) {
                return response()->json(['message' => 'No leads available for export'], 422);
            }

            foreach ($leads as $lead) {
                $lead->update([
                    'category_id' => r('category_id'),
                    'user_id' => Auth::id(),
                    'export_date' => now(),
                ]);

                $lead->histories()->create([
                    'user_id' => Auth::id()
                ]);
            }

            DB::commit();

            return $leads->select('id', 'username');


        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json(['message' => $e->getMessage()], 422);
        }
    }
}
