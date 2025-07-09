<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class BackupDatabase extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'db:backup';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Backup PostgreSQL database';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $dbname = 'instagram_dm_sender';
        $dbuser = 'postgres';
        $dbhost = 'localhost';
        $dbport = 1363;
        $backupDir = 'C:\\Users\\bc';
        $dbpass = 'ufY34numBHHKqoVpcata';

        // Get current date
        $date = now()->format('Y-m-d');
        $backupFile = "{$backupDir}\\{$dbname}_{$date}.backup";
        $backupFileSql = "{$backupDir}\\{$dbname}_{$date}.sql";
        $pgDumpPath = '"C:\\Program Files\\PostgreSQL\\17\\bin\\pg_dump.exe"';
        putenv("PGPASSWORD={$dbpass}");

        // Execute backup command for binary format
        $backupCommand = "{$pgDumpPath} -h {$dbhost} -p {$dbport} -U {$dbuser} -F c -b -v -f \"{$backupFile}\" {$dbname}";
        $sqlCommand = "{$pgDumpPath} -h {$dbhost} -p {$dbport} -U {$dbuser} -F p -b -v -f \"{$backupFileSql}\" {$dbname}";

        // Execute the commands
        $this->info('Starting the database backup...');

        try {
            exec($backupCommand);
            exec($sqlCommand);
            $this->info('Backup completed successfully.');
        } catch (\Exception $e) {
            $this->error('Backup failed: ' . $e->getMessage());
        }
    }
}
