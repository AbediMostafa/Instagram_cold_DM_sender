<?php

namespace App\Console\Commands;

use App\Classes\Modules\LikeAndCommentContext;
use App\Models\Account;
use App\Models\AutomationQueue;
use App\Models\Profile;
use App\Models\Proxy;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;
use Symfony\Component\Console\Command\Command as CommandAlias;

class PushAutomationJobs extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'automation:push-jobs {--limit=100}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Push accounts into automation queue';


    /**
     * The queue's payload
     *
     * @var array
     */
    public array $payload = [
        'profile' => [
            'id' => '',
            'name' => '',
            'profile_id' => '',
        ],
        'proxy' => [
            'id' => '',
            'ip' => '',
            'port' => '',
            'real_ip' => '',
            'type' => '',
        ],
        'account' => [
            'id' => '',
            'username' => '',
            'password' => '',
            'secret_key' => '',
        ],
        'modules' => [
            'classes' => [],
            'object_data' => [],
            'data' => []
        ],
        'timing' => [
            'started_at' => '',
            'finished_at' => '',
            'update_profile_seconds' => '',
            'total_seconds' => '',
        ]
    ];

    protected $profile;
    protected $proxy;
    protected $modules;

    /**
     * Execute the console command.
     */
    public function handle()
    {

        $maxPending = 200;

        $pendingCount = AutomationQueue::query()
            ->where('status', 'pending')
            ->count();

        if ($pendingCount >= $maxPending) {
            Log::channel('automation')->info("Pending queue limit reached ({$pendingCount}/{$maxPending}).");
            return CommandAlias::SUCCESS;
        }

//        $limit = min(
//            (int)$this->option('limit'),
//            $maxPending - $pendingCount
//        );

        $limit = min(
            100,
            $maxPending - $pendingCount
        );

        Log::channel('automation')->info("Going to queue $limit records ({$pendingCount}/{$maxPending}).");

        Account::getNext($limit)
            ->each(function (Account $account) {

                $startTotal = microtime(true);

                try {
                    $this->addAccountToPayload($account);
                    $account->addCli("Selected account ... {$account->username}");

                    $this->profile = Profile::getNext();
                    $account->addCli("Selected profile ... {$this->profile->profile_id}");
                    $this->addProfileToPayload();

                    $this->proxy = Proxy::getFreeProxy($account);
                    $this->addProxyToPayload();

                    $account->updateProfile($this->profile, $this->proxy);

                    $this->payload['timing']['update_profile_seconds'] =
                        round(microtime(true) - $startTotal, 3);

                    $this->addModulesToPayload($account);

                    if (in_array('LikeAndCommentContext', $this->payload['modules']['classes'])) {
                        $module = new LikeAndCommentContext($account);
                        $module->handle();
                        $this->payload['modules']['data']['LikeAndCommentContext'] = $module->payload;
                    }

                    $this->payload['timing']['total_seconds'] =
                        round(microtime(true) - $startTotal, 3);

                    $account->automationQueues()->create([
                        'payload' => $this->payload
                    ]);

                    dump($this->payload);

                } catch (\Exception $e) {
                    $account->addCli("Got problem ... {$e->getMessage()}");
                    Log::channel('automation')->error($e->getMessage());
                }
            });
    }

    public function addProfileToPayload()
    {
        $this->payload['profile'] = [
            'id' => $this->profile->id,
            'name' => $this->profile->title,
            'profile_id' => $this->profile->profile_id,
        ];
    }

    public function addProxyToPayload()
    {
        $this->payload['proxy'] = [
            'id' => $this->proxy->id,
            'ip' => $this->proxy->ip,
            'port' => $this->proxy->port,
            'real_ip' => $this->proxy->real_ip,
            'type' => $this->proxy->type,
        ];
    }

    public function addAccountToPayload($account)
    {
        $this->payload['account'] = [
            'id' => $account->id,
            'username' => $account->username,
            'password' => $account->password,
            'secret_key' => $account->secret_key,
        ];
    }

    public function addModulesToPayload($account)
    {
        $this->modules = $account->service
            ?->workflows()
            ?->first()
            ?->modules;

        if ($this->modules->isEmpty()) {
            throw new \Exception('There is no module assigned to this account');
        }

        $this->payload['modules']['classes'] = $this->modules->pluck('class_name')->toArray();

        $this->modules?->each(function ($module) {
            $this->payload['modules']['object_data'][$module->class_name] = [
                'id' => $module->id,
                'class_name' => $module->class_name,
                'priority' => $module->priority,
            ];
        });
    }
}
