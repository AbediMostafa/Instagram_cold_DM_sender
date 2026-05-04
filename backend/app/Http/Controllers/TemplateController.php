<?php

namespace App\Http\Controllers;

use App\Models\Account;
use App\Models\AccountTemplate;
use App\Models\Color;
use App\Models\Template;
use Carbon\Carbon;
use Illuminate\Support\Facades\Storage;

class TemplateController extends Controller
{
    public function index()
    {

        $query = Template::query()
            ->where('type', r('type'))
            ->with('tags:id,title')
            ->when(r('type') === 'carousel', function ($query) {
                $query->where('color_id', r('color'))
                    ->orderBy('color_id')
                    ->orderBy('uid');
            })
            ->when(r('tags'), function ($query) {
                $tags = r('tags');
                $query->whereHas('tags', function ($q) use ($tags) {
                    $q->whereIn('tags.id', $tags);
                }, '=', count($tags));
            })
            // Optional filter to show only custom templates.
            // Custom templates are uploads marked with is_custom=true that
            // get prioritized by the worker and tracked individually for stats.
            ->when(r('custom_only'), function ($query) {
                $query->where('is_custom', true);
            })
            ->orderBy('id', 'asc');

        $paginator = $query->paginate(
            config('data.pagination.each_page.templates')
        );

        $data = match (r('type')) {
            'carousel', 'video-post' => $paginator
                ->getCollection()
                ->groupBy('carousel_id')
                ->values(),

            default => $paginator->getCollection(),
        };

        return [
            'data' => $data,
            'meta' => [
                'current_page' => $paginator->currentPage(),
                'last_page'    => $paginator->lastPage(),
                'per_page'     => $paginator->perPage(),
                'total'        => $paginator->total(),
            ],
            'type' => r('type'),
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

        $template = Template::query()->create([
            'text' => $filePath,
            'type' => $mediaType,
            'sub_type' => $subType,
            'carousel_id' => $carouselId,
            'uid' => $mediaType === 'carousel' ? r('uid') : null,
            'color_id' => $colorId,
            'category_id' => r('category'),
            'caption' => r('caption'),
            // Mark uploads as custom for image-post and video-post.
            // Custom templates are assignable to specific accounts and
            // are prioritized by the worker over Lead-based selection.
            'is_custom' => in_array($mediaType, ['image-post', 'video-post']),
        ]);

        !empty(r('tags')) && $template->tags()->attach(r('tags'));

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
            ->with('tags:id,title')
            ->select('id', 'category_id', 'caption')
            ->findOrFail(r('id'));
    }

    public function update()
    {
        return tryCatch(
            function () {
                $template = Template::query()->findOrFail(r('id'));

                // Update scalar fields. Pivot relationships and id must
                // be excluded so they don't end up as columns.
                $template->update(
                    r()->except(['id', 'tags', 'category'])
                );

                // Sync tags when the request includes a tags array.
                // Pass an empty array to clear all tags. Skip the call
                // entirely when the field is missing so we don't wipe
                // tags from callers that aren't aware of this contract.
                if (r()->has('tags')) {
                    $tagIds = r('tags', []);
                    $template->tags()->sync($tagIds);
                }

                return $template->load('tags:id,title');
            },
            'Template updated successfully',
        );
    }

    public function getTemplate()
    {
        $account = Account::query()->findOrFail(r('id'));
        $tagIds = $account->tags()->pluck('id')->toArray();
        $type = r('type');

        return Template::query()
            ->where('type', $type)
            ->whereHas('tags')//templates that have at least one tag
            ->whereDoesntHave('tags', fn($q) => $q->whereNotIn('tags.id', $tagIds))
            ->inRandomOrder()
            ->first();
    }

    public function attachTag()
    {

        return tryCatch(

            function () {

                $accounts = Template::query()
                    ->whereIn('id', r('templateIds'))
                    ->get();

                foreach ($accounts as $account) {
                    $account->tags()->syncWithoutDetaching(r('tagIds'));
                }
            },
            'Tags attached successfully'
        );
    }


    public function stats()
    {
        $templateId = r('id');

        // Total aggregated stats (only completed)
        $totals = AccountTemplate::where('template_id', $templateId)
            ->where('status', 'completed')
            ->selectRaw('
            COUNT(*) as total_posts,
            SUM(like_count) as total_likes,
            SUM(comment_count) as total_comments,
            SUM(view_count) as total_views,
            SUM(save_count) as total_saves,
            SUM(repost_count) as total_reposts
        ')
            ->first();

        // Lightweight counter for in-flight posts so the assign modal
        // can show "X posted, Y in progress" without a separate call.
        $processingCount = AccountTemplate::where('template_id', $templateId)
            ->where('status', 'processing')
            ->count();

        // Per-account breakdown
        $breakdown = AccountTemplate::where('template_id', $templateId)
            ->where('status', 'completed')
            ->with('account:id,username,profile_pic_url')
            ->get([
                'id', 'account_id', 'url',
                'like_count', 'comment_count', 'view_count',
                'save_count', 'repost_count', 'created_at', 'updated_at'
            ]);

        return [
            'template_id'      => (int) $templateId,
            'totals'           => $totals,
            'processing_count' => $processingCount,
            'breakdown'        => $breakdown,
        ];
    }

    /**
     * Assign a custom template to one or more accounts.
     * Creates account_template records with status='pending' so the
     * worker can pick them up and prioritize them over Lead-based posts.
     *
     * Accepted input:
     *   - template_id   (required)
     *   - account_ids[] (when all_active is false)
     *   - all_active    (boolean, when true assigns to every active account)
     *
     * Duplicate prevention: any existing record for the same
     * (template_id, account_id) pair is skipped, regardless of its status.
     * Returns the per-call counters so the UI can report progress.
     */
    public function assignAccounts()
    {
        r()->validate([
            'template_id'   => 'required|integer|exists:templates,id',
            'account_ids'   => 'array',
            'account_ids.*' => 'integer|exists:accounts,id',
            'all_active'    => 'boolean',
        ]);

        $template = Template::query()->findOrFail(r('template_id'));

        // Only image-post and video-post are assignable for now.
        if (!in_array($template->type, ['image-post', 'video-post'])) {
            abort(422, 'Only image-post and video-post templates can be assigned');
        }

        // For video-post, the assignment target must be the video record.
        // The worker resolves the cover image later via carousel_id.
        if ($template->type === 'video-post' && $template->sub_type !== 'video') {
            abort(422, 'For video-post, assignment must target the video sub_type template');
        }

        // Resolve target account IDs.
        if (r('all_active')) {
            $accountIds = Account::query()
                ->where('instagram_state', 'active')
                ->pluck('id')
                ->toArray();
        } else {
            $accountIds = r('account_ids', []);
        }

        if (empty($accountIds)) {
            return [
                'assigned' => 0,
                'skipped'  => 0,
            ];
        }

        // Skip accounts that already have any record for this template.
        // Duplicates across pending/processing/completed are not allowed.
        // Chunk the IN clause to avoid query size limits for very
        // large account sets (e.g. when all_active=true on big DBs).
        $existingAccountIds = [];
        $checkChunkSize = 1000;

        foreach (array_chunk($accountIds, $checkChunkSize) as $chunk) {
            $found = AccountTemplate::query()
                ->where('template_id', $template->id)
                ->whereIn('account_id', $chunk)
                ->pluck('account_id')
                ->toArray();

            $existingAccountIds = array_merge($existingAccountIds, $found);
        }

        $newAccountIds = array_values(array_diff($accountIds, $existingAccountIds));

        if (empty($newAccountIds)) {
            return [
                'assigned' => 0,
                'skipped'  => count($existingAccountIds),
            ];
        }

        // Bulk insert pending records in chunks to avoid hitting
        // database packet size limits when assigning to thousands
        // of accounts at once.
        $now = Carbon::now();
        $insertChunkSize = 500;

        foreach (array_chunk($newAccountIds, $insertChunkSize) as $chunk) {
            $rows = array_map(fn($accountId) => [
                'account_id'  => $accountId,
                'template_id' => $template->id,
                'status'      => 'pending',
                'created_at'  => $now,
                'updated_at'  => $now,
            ], $chunk);

            AccountTemplate::query()->insert($rows);
        }

        return [
            'assigned' => count($newAccountIds),
            'skipped'  => count($existingAccountIds),
        ];
    }

    /**
     * Return the list of accounts currently assigned to this template
     * with status='pending'. Used by the assignment modal to render
     * the "Currently assigned" section so the user can review and
     * unassign individual accounts before they get processed.
     *
     * Cursor-based pagination keeps the response small and stable even
     * when thousands of pending rows exist. The optional search filter
     * narrows results to usernames containing the given substring.
     *
     * Accepted input:
     *   - template_id (required)
     *   - before_id   (optional, returns rows with id < before_id)
     *   - search      (optional, substring match against username)
     *   - per_page    (optional, default 100, max 200)
     *
     * Returns:
     *   - data:         page of records, newest first
     *   - has_more:     whether more rows exist beyond this page
     *   - next_before:  pass this as before_id on the next call
     *   - total:        total pending rows for this template (unfiltered)
     */
    public function assignedAccounts()
    {
        r()->validate([
            'template_id' => 'required|integer|exists:templates,id',
            'before_id'   => 'nullable|integer',
            'search'      => 'nullable|string',
            'per_page'    => 'nullable|integer|min:1|max:200',
        ]);

        $templateId = (int) r('template_id');
        $beforeId   = r('before_id');
        $search     = trim((string) r('search', ''));
        $perPage    = (int) r('per_page', 100);

        $query = AccountTemplate::query()
            ->where('template_id', $templateId)
            ->where('status', 'pending')
            ->with('account:id,username,profile_pic_url')
            ->select('id', 'account_id', 'template_id', 'status');

        // Cursor: keep going from the last id we returned. Newest
        // rows have the largest ids so we walk backwards.
        if ($beforeId) {
            $query->where('id', '<', $beforeId);
        }

        // Username search runs through a join because the username
        // lives on the accounts table, not on the pivot.
        if ($search !== '') {
            $query->whereHas('account', function ($q) use ($search) {
                $q->where('username', 'like', "%{$search}%");
            });
        }

        $rows = $query
            ->orderBy('id', 'desc')
            ->limit($perPage + 1)
            ->get();

        // We fetched one extra row to detect whether more exist
        // without a separate COUNT query.
        $hasMore = $rows->count() > $perPage;
        if ($hasMore) {
            $rows = $rows->take($perPage);
        }

        $nextBefore = $hasMore ? $rows->last()->id : null;

        // Total pending count (unfiltered) so the modal can keep the
        // header accurate regardless of search input.
        $total = AccountTemplate::query()
            ->where('template_id', $templateId)
            ->where('status', 'pending')
            ->count();

        return [
            'data'        => $rows,
            'has_more'    => $hasMore,
            'next_before' => $nextBefore,
            'total'       => $total,
        ];
    }

    /**
     * Remove pending assignments for this template.
     * Only records with status='pending' are deleted; processing and
     * completed records are protected so the worker is not interrupted
     * and stats are not lost.
     *
     * Accepted input:
     *   - template_id    (required)
     *   - account_ids[]  (when unassign_all is false)
     *   - unassign_all   (boolean, when true removes every pending record
     *                     for this template)
     */
    public function unassignAccounts()
    {
        r()->validate([
            'template_id'   => 'required|integer|exists:templates,id',
            'account_ids'   => 'array',
            'account_ids.*' => 'integer|exists:accounts,id',
            'unassign_all'  => 'boolean',
        ]);

        $templateId = (int) r('template_id');

        $query = AccountTemplate::query()
            ->where('template_id', $templateId)
            ->where('status', 'pending');

        if (r('unassign_all')) {
            $deleted = $query->delete();

            return [
                'unassigned' => $deleted,
            ];
        }

        $accountIds = r('account_ids', []);

        if (empty($accountIds)) {
            return [
                'unassigned' => 0,
            ];
        }

        // Chunk the IN clause for very large lists. Each chunk runs its
        // own DELETE so the total deleted count is the sum across chunks.
        $totalDeleted = 0;
        $deleteChunkSize = 1000;

        foreach (array_chunk($accountIds, $deleteChunkSize) as $chunk) {
            $totalDeleted += AccountTemplate::query()
                ->where('template_id', $templateId)
                ->where('status', 'pending')
                ->whereIn('account_id', $chunk)
                ->delete();
        }

        return [
            'unassigned' => $totalDeleted,
        ];
    }
}
