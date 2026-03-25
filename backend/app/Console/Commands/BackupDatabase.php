<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\File;

class BackupDatabase extends Command
{
    protected $signature = 'db:backup';
    protected $description = 'Backup PostgreSQL database';

    public function handle()
    {
        $dbname = config('database.connections.pgsql.database');
        $dbuser = config('database.connections.pgsql.username');
        $dbhost = config('database.connections.pgsql.host', 'localhost');
        $dbport = config('database.connections.pgsql.port', 5432);
        $dbpass = config('database.connections.pgsql.password');
        $backupDir = env('BACKUP_DIR', 'C:\\Users\\bc');
        $pgDumpPath = env('PG_DUMP_PATH', 'C:\\Program Files\\PostgreSQL\\18\\bin\\pg_dump.exe');

        // Ensure backup directory exists
        if (!File::isDirectory($backupDir)) {
            File::makeDirectory($backupDir, 0755, true);
            $this->info("Created backup directory: {$backupDir}");
        }

        $date = now()->format('Y-m-d');
        $backupFile = "{$backupDir}\\{$dbname}_{$date}.backup";
        $backupFileSql = "{$backupDir}\\{$dbname}_{$date}.sql";

        putenv("PGPASSWORD={$dbpass}");

        $baseCmd = "\"{$pgDumpPath}\" -h {$dbhost} -p {$dbport} -U {$dbuser} -b -v";

        $this->info('Starting database backup...');

        // Binary format
        exec("{$baseCmd} -F c -f \"{$backupFile}\" {$dbname} 2>&1", $output1, $code1);

        if ($code1 !== 0) {
            $this->error("Binary backup failed (exit code: {$code1})");
            $this->error(implode("\n", $output1));
            return 1;
        }

        $this->info("Binary backup: {$backupFile}");

        // SQL format
        exec("{$baseCmd} -F p -f \"{$backupFileSql}\" {$dbname} 2>&1", $output2, $code2);

        if ($code2 !== 0) {
            $this->error("SQL backup failed (exit code: {$code2})");
            $this->error(implode("\n", $output2));
            return 1;
        }

        $this->info("SQL backup: {$backupFileSql}");
        $this->info('Backup completed successfully.');

        // Clean old backups (keep last 7 days)
        $this->cleanOldBackups($backupDir, $dbname, 7);

        return 0;
    }

    private function cleanOldBackups(string $dir, string $dbname, int $keepDays)
    {
        $threshold = now()->subDays($keepDays);

        foreach (File::files($dir) as $file) {
            $filename = $file->getFilename();

            if (!str_starts_with($filename, $dbname)) {
                continue;
            }

            if ($file->getMTime() < $threshold->timestamp) {
                File::delete($file->getPathname());
                $this->info("Deleted old backup: {$filename}");
            }
        }
    }
}
