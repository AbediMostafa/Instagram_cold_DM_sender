<?php

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


function startInfiniteScripts($threads)
{
    $python = 'python'; // Adjust to your Python interpreter
    $scriptPath = dirname(base_path()) . '\script\t.py'; // Path to the Python script

    // Create an array to hold the processes and their PIDs
    $processes = [];
    $pids = [];

    try {
        // Launch Python processes
        for ($i = 1; $i <= $threads; $i++) {
            $process = new Process([$python, $scriptPath]);
            $process->setTimeout(null);

            // Start the process asynchronously
            $process->start(function ($type, $buffer) use ($i) {
                // Handle real-time output
                if (Process::ERR === $type) {
                    dump("Process {$i} Error: " . $buffer);
                } else {
                    dump("Process {$i} Output: " . $buffer);
                }
            });

            // Store the process and PID
            $processes[] = $process;
            $pids[] = $process->getPid();
        }

        // Output PIDs for reference
        dump("Launched Infinite Scripts with PIDs: " . implode(', ', $pids));

        // Optionally wait and capture final output
        foreach ($processes as $index => $process) {
            $process->wait(); // Wait for the process to finish

            dump("Process {$index} Final Output: " . $process->getOutput());
            dump("Process {$index} Final Error: " . $process->getErrorOutput());
        }
    } catch (\Exception $e) {
        dump("Error: " . $e->getMessage());
    }
}

function terminateProcesses(array $pids)
{
    foreach ($pids as $pid) {
        try {
            // Execute the taskkill command for each PID
            $process = new Process(["taskkill", "/PID", $pid, "/F"]);
            $process->run();

            // Check if the command succeeded
            if ($process->isSuccessful()) {
                dump("Process PID {$pid} terminated successfully.");
            } else {
                dump("Failed to terminate PID {$pid}: " . $process->getErrorOutput());
            }
        } catch (\Exception $e) {
            dump("Error terminating PID {$pid}: " . $e->getMessage());
        }
    }
}


function showProcesses(array $pids)
{
    foreach ($pids as $pid) {
        // Verify the process name before termination
        $processInfo = shell_exec("tasklist /FI \"PID eq {$pid}\"");
        dump($processInfo);
    }
}

function likeOperator()
{
    Dotenv::createImmutable(__DIR__ . "/..")->load();

    $dbConnection = env('DB_CONNECTION', 'mysql'); // Default to MySQL if not set

    return ($dbConnection === 'pgsql') ? 'ILIKE' : 'LIKE'; // Use ILIKE for PostgreSQL
}
