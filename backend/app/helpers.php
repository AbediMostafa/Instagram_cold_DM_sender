<?php

use App\Models\Balance;
use Carbon\Carbon;
use Dotenv\Dotenv;
use Illuminate\Support\Facades\Http;
use JetBrains\PhpStorm\ArrayShape;
use Morilog\Jalali\Jalalian;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

if (!function_exists('jsonError')) {
    /**
     * Return error status and message to the front
     *
     * @param $msg
     * @param bool|array $additional
     * @return array
     */
    #[ArrayShape(['withResponse' => "bool", 'status' => "int", 'msg' => ""])]
    function jsonError($msg, bool|array $additional = []): array
    {
        return $additional ?
            [
                'withResponse' => true,
                'status' => 0,
                'msg' => $msg,
                ...$additional
            ] :
            [
                'withResponse' => true,
                'status' => 0,
                'msg' => $msg
            ];
    }
}

if (!function_exists('jsonSuccess')) {
    /**
     * Return success status and message to the front
     *
     * @param $msg
     * @param bool|array $additional
     * @return array
     */
    #[ArrayShape(['status' => "int", 'msg' => "string"])]
    function jsonSuccess($msg, bool|array $additional = []): array
    {
        return $additional ?
            [
                'withResponse' => true,
                'status' => 1,
                'msg' => $msg,
                ...$additional
            ] :
            [
                'withResponse' => true,
                'status' => 1,
                'msg' => $msg,
            ];
    }
}

if (!function_exists('tryCatch')) {

    /**
     * Simplifies try catch block
     *
     * @param $callB
     * @param $successMsg
     * @return array
     */
    function tryCatch($callB, $successMsg)
    {
        try {
            $callB();

            return jsonSuccess($successMsg);

        } catch (Exception $e) {

            if (get_class($e) === 'Symfony\Component\HttpKernel\Exception\HttpException') {
                throw new HttpException(422, $e->getMessage());
            }

            /**
             * TODO : in production mode replace with $errorMsg
             */
            return jsonError($e->getMessage());
        }
    }
}

/**
 * A shorthand of request method
 *
 * @return array|\Illuminate\Contracts\Foundation\Application|\Illuminate\Http\Request|mixed|string|null
 */
function r($value = ''): mixed
{
    return $value ? request($value) : request();
}

function runPythonProcess($pythonFile, $commandId)
{
    $path = base_path("../script/$pythonFile");
    $process = new Process(['python', $path, $commandId]);
    $process->setTimeout(400);
    $process->run();

//    if (!$process->isSuccessful()) {
//        throw new ProcessFailedException($process);
//    }

    return jsonSuccess($process->getOutput());
}


function likeOperator()
{
    Dotenv::createImmutable(__DIR__ . "/..")->load();

    $dbConnection = env('DB_CONNECTION', 'mysql'); // Default to MySQL if not set

    return ($dbConnection === 'pgsql') ? 'ILIKE' : 'LIKE'; // Use ILIKE for PostgreSQL
}

function deductBalance($actionType, $count = 1)
{
    $rates = [
        'comment' => 0.0003,
        'view_story' => 0.00005,
        'view_all_stories' => 0.00005,
        'save_post' => 0.00004,
    ];

    $rate = $rates[$actionType] ?? 0.00005;
    $totalCharge = $rate * $count;

    $balance = Balance::where('customer', 'sadeghi')->first();
    if ($balance) {
        $balance->balance -= $totalCharge;
        $balance->save();
    }
}
