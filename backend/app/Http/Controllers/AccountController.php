<?php

namespace App\Http\Controllers;

use App\Classes\Fingerprint;
use App\Models\Account;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use imseyed\Auth2FA;

class AccountController extends Controller
{
    public function index()
    {
        if (r('dateRange')) {
            $startDate = Carbon::parse(r('dateRange')[0])->startOfDay();
            $endDate = Carbon::parse(r('dateRange')[1])->endOfDay();
        } else {
            $startDate = Carbon::today()->startOfDay();
            $endDate = Carbon::today()->endOfDay();
        }

        $accounts = Account::query()
            ->select(
                'id', 'avatar_changed', 'username', 'instagram_state', 'email', 'phone',
                'name', 'password', 'email_password', 'created_at', 'category_id', 'service_id',
                'country_id', 'secret_key', 'proxy_id', 'profile_id', 'has_enough_posts', 'name',
                'app_state')
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
                'service:id,title',
                'country:id,name,country_code',
                'tags:id,title',
                'warnings' => function ($query) use ($startDate, $endDate) {
                    $query->select('created_at', 'account_id', 'cause')
                        ->orderByDesc('created_at');
                }
            ])
            ->when(
                r('filter'),
                fn($_) => $_->whereIn('instagram_state', r('filter'))
            )
            ->when(
                r('uploadPostFilter'),
                fn($_) => $_->whereIn('upload_post_status', r('uploadPostFilter'))
            )
            ->when(
                r('countries'),
                fn($_) => $_->whereIn('country_id', r('countries'))
            )
            ->when(
                r('search'),
                function ($_) {
                    if (r('type') === 'proxy') {
                        $_->whereHas('proxy', fn($__) => $__->where('ip', likeOperator(), '%' . r('search') . '%'));
                    }

                    if (r('type') === 'account') {
                        $_->where('username', likeOperator(), '%' . r('search') . '%');
                    }

                    if (r('type') === 'prolfile') {
                        $_->whereHas('profile', fn($__) => $__->where('title', likeOperator(), '%' . r('search') . '%'));
                    }

                    if (r('type') === 'accountId') {
                        $_->where('id', likeOperator(), '%' . r('search') . '%');
                    }

                    if (r('type') === 'phone') {
                        $_->where('phone', likeOperator(), '%' . r('search') . '%');
                    }

                    if (r('type') === 'uploadPost') {
                        $_->where('upload_post_username', likeOperator(), '%' . r('search') . '%');
                    }
                }
            )
            ->when(r('tags'), function ($query) {
                $tags = r('tags');

                $query->whereHas('tags', function ($q) use ($tags) {
                    $q->whereIn('tags.id', $tags);
                }, '=', count($tags));
            })
            ->when(r('services'), function ($query) {
                $services = r('services');

                $query->whereHas('service', function ($q) use ($services) {
                    $q->whereIn('id', $services);
                }, '=', count($services));
            })
            ->orderBy('id', 'DESC')
            ->paginate(
                config('data.pagination.each_page.accounts')
            );

        $accounts->getCollection()->transform(function ($account) {
            $account->created_at_ago = $account->created_at?->diffForHumans();

            $latestWarningCreatedAt = $account->warnings->first()->created_at ?? null;
            $account->latest_warning_created_at_ago = $latestWarningCreatedAt ? Carbon::parse($latestWarningCreatedAt)->diffForHumans() : 'No warnings';

            return $account;
        });

        return $accounts;
    }

    public function view()
    {
        return Account::query()->select(
            'username', 'password', 'name', 'bio', 'id', 'avatar_changed',
            'instagram_state', 'app_state', 'is_active', 'created_at', 'country_id')
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
                'country:id,name,country_code',
            ])
            ->withCount([
                'commands as following_count' => fn($_) => $_->where('type', 'follow')->where('state', 'success'),
                'commands as image_post_count' => fn($_) => $_->where('type', 'post image')->where('state', 'success'),
                'commands as dm_count' => fn($_) => $_->where('type', 'dm follow up')->where('state', 'success'),
                'commands as successful_commands' => fn($_) => $_->where('state', 'success'),
                'commands as total_commands',
            ])
            ->find(r('id'));
    }

    public function getAccount()
    {
        return Account::query()->select(
            'username', 'password', 'name', 'bio',
            'instagram_state', 'app_state', 'color_id', 'is_used',
            'avatar_changed', 'username_changed', 'initial_posts_deleted',
            'has_enough_posts', 'next_login', 'country_id'
        )
            ->find(r('id'));
    }

    public function create()
    {
        if (request('bulk_insertion')) {
            r()->validate([
                'accounts' => 'required',
            ]);
        } else {
            r()->validate([
                'username' => 'required|unique:accounts',
                'password' => 'required'
            ]);
        }

        return tryCatch(
            fn() => r('bulk_insertion') ? Account::createBulk() : Account::createOne(),
            'Account created successfully',
        );
    }

    public function delete()
    {
        return tryCatch(function () {

            Account::query()
                ->whereIn('id', r('ids'))
                ->delete();
        },
            'Account(s) deleted successfully'
        );
    }

    public function edit()
    {
        r()->validate([
            'username' => 'required|unique:accounts,username,' . r('id')
        ]);

        return tryCatch(
            fn() => Account::query()
                ->where('id', r('id'))
                ->update([
                    'username' => r('username'),
                    'password' => r('password'),
                    'instagram_state' => r('instagram_state'),
                    'color_id' => r('color_id'),
                    'is_used' => r('is_used'),
                    'avatar_changed' => r('avatar_changed'),
                    'username_changed' => r('username_changed'),
                    'has_enough_posts' => r('has_enough_posts'),
                ]),
            'Account updated successfully',
        );
    }

    public function setCategory()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('accountIds'))
                ->update([
                    'category_id' => r('categoryId'),
                ]),
            'Account updated successfully',
            'Problem updating account',
        );
    }

    public function deleteWarning()
    {
        return tryCatch(
            function () {
                $accounts = Account::whereIn('id', r('ids'))->get();

                foreach ($accounts as $account) {
                    $account->warnings()->delete();
                }
            },
            'Warning(s) deleted successfully',
            'Problem updating account',
        );

    }

    public function makeActive()
    {
        return tryCatch(
            fn() => Account::whereIn('id', r('ids'))->get()
                ->each(fn(Account $account) => $account->makeActive()),
            'Warning(s) deleted successfully',
            'Problem updating account',
        );
    }

    public function clearNextLogin()
    {
        return tryCatch(
            function () {
                Account::whereIn('id', r('ids'))
                    ->get()
                    ->each(function (Account $account) {
                        $account->next_login = null;
                        $account->save();
                    });
            },
            'Next login deleted successfully',
            'Problem updating account',
        );

    }

    public function fetchAccounts()
    {
        return Account::query()
            ->select('id', 'username')
            ->where('username', 'like', '%' . request('q') . '%')
            ->get();
    }

    public function clearProfile()
    {
        return tryCatch(
            function () {
                $accounts = Account::whereIn('id', r('ids'))->get();

                foreach ($accounts as $account) {
                    $account->profile_id = null;
                    $account->save();
                }
            },
            'Profile(s) deleted successfully',
            'Problem updating account',
        );
    }

    public function get2faCode()
    {
        try {

            return r('secretKey') ? Auth2FA::TOTP(r('secretKey')) : '';
        } catch (\Exception $exception) {

            return "Error getting 2fa code : " . $exception->getMessage();
        }
    }

    public function getProxyApi()
    {
        return Account::query()->find(r('id'))->getProxy();
    }

    public function changeProfileProxyToCustom()
    {
        try {
            Account::query()->whereIn('id', r('ids'))
                ->get()
                ->each(
                    fn(Account $account) => $account->updateProfileProxyToCustom()
                );
            return jsonSuccess('Account(s) Profile proxies updated successfully');

        } catch (\Exception $exception) {
            return jsonError($exception->getMessage() . $exception->getTraceAsString());
        }
    }

    public function startProfile()
    {
        try {

            foreach (r('ids') as $id) {

                $account = Account::find($id);
                $account->makeActive();
                runPythonProcess('new.py', $account->id);
            }

            return jsonSuccess('Profiles started ');

        } catch (Exception $e) {

            return jsonError($e->getMessage());
        }
    }

    /**
     * Set upload_post_status to 'pending' for selected accounts.
     * This marks them for the Python worker to connect to Upload-Post.
     */
    public function uploadPostConnect()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('ids'))
                ->update(['upload_post_status' => 'pending']),
            'Account(s) marked for Upload-Post connection',
        );
    }

    /**
     * Set upload_post_status to 'disconnecting' for selected accounts.
     * This marks them for the Python worker to disconnect from Upload-Post.
     */
    public function uploadPostDisconnect()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('ids'))
                ->update(['upload_post_status' => 'disconnecting']),
            'Account(s) marked for Upload-Post disconnection',
        );
    }

    /**
     * Reset upload_post_status to 'none' for selected accounts.
     * upload_post_username is preserved so the same profile number can be reused if reconnected.
     * Useful when status is incorrectly set (e.g. shows 'connected' but isn't actually connected).
     */
    public function resetUploadPostStatus()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('ids'))
                ->update(['upload_post_status' => 'none']),
            'Upload-Post status reset to none',
        );
    }

    /**
     * Toggle Upload-Post connection for a single account.
     * Sets the appropriate status and runs the Python script which handles
     * both connect and disconnect flows via the browser (with proxy).
     *
     * Based on current status:
     *   - none/failed/disconnecting -> set to 'pending' and run script
     *   - connected                 -> set to 'disconnecting' and run script
     *   - pending/connecting        -> return error (already in progress)
     */
    public function toggleUploadPost()
    {
        try {
            $account = Account::find(r('id'));

            \Log::info('[UploadPost Toggle] Started', [
                'account_id' => $account->id,
                'username' => $account->username,
                'current_status' => $account->upload_post_status,
                'upload_post_username' => $account->upload_post_username,
            ]);

            if (in_array($account->upload_post_status, ['none', 'failed', 'disconnecting'])) {
                $account->upload_post_status = 'pending';
                $account->save();

                \Log::info('[UploadPost Toggle] Status set to pending, running script...', [
                    'account_id' => $account->id,
                ]);

                $path = base_path("../script/upload_post_connect.py");
                $process = new \Symfony\Component\Process\Process(['python', $path, (string)$account->id]);
                $process->setTimeout(400);
                $process->run();

                \Log::info('[UploadPost Toggle] Script finished', [
                    'account_id' => $account->id,
                    'exit_code' => $process->getExitCode(),
                    'stdout' => $process->getOutput(),
                    'stderr' => $process->getErrorOutput(),
                ]);

                return jsonSuccess('Upload-Post connect started');

            } elseif ($account->upload_post_status === 'connected') {
                // Disconnect: call Upload-Post API directly from PHP.
                // No browser needed - this also handles challenging accounts that can't login.
                \Log::info('[UploadPost Toggle] Disconnecting via API...', [
                    'account_id' => $account->id,
                    'upload_post_username' => $account->upload_post_username,
                ]);

                if ($account->upload_post_username) {
                    $apiKey = env('UPLOAD_POST_API_KEY');

                    $response = Http::withHeaders([
                        'Authorization' => 'ApiKey ' . $apiKey,
                        'Content-Type' => 'application/json',
                    ])->delete('https://api.upload-post.com/api/uploadposts/users', [
                        'username' => $account->upload_post_username,
                    ]);

                    \Log::info('[UploadPost Toggle] API delete response', [
                        'account_id' => $account->id,
                        'status' => $response->status(),
                        'body' => $response->body(),
                    ]);
                }

                // Reset status but keep upload_post_username (numbers are never reused)
                $account->upload_post_status = 'none';
                $account->save();

                return jsonSuccess('Upload-Post disconnected');

            } else {
                \Log::warning('[UploadPost Toggle] Skipped - already in progress', [
                    'account_id' => $account->id,
                    'current_status' => $account->upload_post_status,
                ]);

                return jsonError('Account is currently ' . $account->upload_post_status . ', please wait');
            }

        } catch (\Exception $e) {
            \Log::error('[UploadPost Toggle] Exception', [
                'account_id' => r('id'),
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString(),
            ]);

            return jsonError($e->getMessage());
        }
    }

    public function assignFingerprint()
    {
        $fingerprint = new Fingerprint();

        $accountsQuery = Account::query();

        r('ids') && $accountsQuery->whereIn('id', request('ids'));

        return tryCatch(
            fn() => $accountsQuery->get()
                ->each(function (Account $account) use ($fingerprint) {
                    $account->fingerprint = $fingerprint->generate();
                    $account->save();
                }),
            'Fingerprints assigned successfully',
        );
    }

    public function findAccounts()
    {
        $queryStr = str_replace(['\\', '_', '%'], ['\\\\', '\\_', '\\%'], request('query'));

        $query = Account::query()
            ->select('id', 'username', 'phone')
            ->whereRaw("username ILIKE ? ESCAPE '\\'", ["%{$queryStr}%"]);

        return [
            'accounts' => $query->orderBy('username')->get(),
            'count' => $query->count(),
        ];
    }

    public function attachTag()
    {

        return tryCatch(

            function () {

                $accounts = Account::query()
                    ->whereIn('id', r('accountIds'))
                    ->get();

                foreach ($accounts as $account) {
                    $account->tags()->syncWithoutDetaching(r('tagIds'));
                }
            },
            'Tags attached successfully'
        );
    }

    public function attachService()
    {
        return tryCatch(function () {

            $serviceIds = r('serviceIds');

            abort_if(count($serviceIds) > 1, 422, 'Only one service can be assigned to an account.');
            abort_if(empty($serviceIds), 422, 'There is no service selected');

            Account::query()
                ->whereIn('id', r('accountIds'))
                ->get()
                ->each(fn($account) => $account->update(['service_id' => $serviceIds[0]]));

        }, 'Service attached successfully');
    }

    public function detachService()
    {
        return tryCatch(function () {

            Account::query()
                ->whereIn('id', r('accountIds'))
                ->get()
                ->each(fn($account) => $account->update(['service_id' => null]));

        }, 'Service detached successfully');
    }

    public function attachCountry()
    {
        return tryCatch(function () {

            $countryId = r('countryId');

            abort_if(empty($countryId), 422, 'No country selected');

            Account::query()
                ->whereIn('id', r('accountIds'))
                ->update(['country_id' => $countryId]);

        }, 'Country assigned successfully');
    }

    public function detachCountry()
    {
        return tryCatch(function () {

            Account::query()
                ->whereIn('id', r('accountIds'))
                ->update(['country_id' => null]);

        }, 'Country detached successfully');
    }

    public function detachTag()
    {
        return tryCatch(

            function () {

                $accounts = Account::query()
                    ->whereIn('id', r('accountIds'))
                    ->get();

                $tagIds = r('tagIds');

                if (!empty($tagIds)) {
                    foreach ($accounts as $account) {
                        $account->tags()->detach($tagIds);
                    }
                }
            },
            'Tags detached successfully'
        );
    }

    public function resetIsUsed()
    {
        return tryCatch(
            fn() => Account::query()->update(['is_used' => 0]),
            'Is used reset successfully'
        );
    }
}
