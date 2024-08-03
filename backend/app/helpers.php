<?php

use Carbon\Carbon;
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
    $process = new Process(['python3', $path, $commandId]);
    $process->run();

    if (!$process->isSuccessful()) {
        throw new ProcessFailedException($process);
    }

    return jsonSuccess($process->getOutput());
}

