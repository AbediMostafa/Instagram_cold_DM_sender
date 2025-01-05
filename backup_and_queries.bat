@echo off
set dbname=instagram_dm_sender
set dbuser=postgres
set dbhost=localhost
set dbport=1363
set backup_dir=C:\Users\bc
set pg_dump_path="C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
set psql_path="C:\Program Files\PostgreSQL\17\bin\psql.exe"

:: Get current date and time
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set YYYY=%dt:~0,4%
set MM=%dt:~4,2%
set DD=%dt:~6,2%

set backup_file=%backup_dir%\%dbname%_%YYYY%-%MM%-%DD%.backup
set backup_file_sql=%backup_dir%\%dbname%_%YYYY%-%MM%-%DD%.sql

:: Run pg_dump for backup (be sure to correctly quote the path)
%pg_dump_path% -h %dbhost% -p %dbport% -U %dbuser% -F c -b -v -f "%backup_file%" %dbname%
%pg_dump_path% -h %dbhost% -p %dbport% -U %dbuser% -F p -b -v -f "%backup_file_sql%" %dbname%

:: Check if backup was successful
if %ERRORLEVEL% NEQ 0 (
    echo Backup failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Backup completed successfully at %backup_file%

:: Run a specific query on the database (optional)
%psql_path% -h %dbhost% -p %dbport% -U %dbuser% -d %dbname% -c "DELETE FROM clis where id=10464sdfdsf;" >> "%backup_dir%\query_output_%YYYY%-%MM%-%DD%.log"
exit
