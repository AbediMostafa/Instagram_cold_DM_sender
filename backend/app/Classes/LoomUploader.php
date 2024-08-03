<?php

namespace App\Classes;


use App\Models\Loom;
use Carbon\Carbon;
use \Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

class LoomUploader
{
    public static array $messages =[
        'file_exists'=>'A file with the same name already exists.',
        'storage_failed'=>'File storage failed',
        'database_failed'=>'Database operation failed',
    ];
    public UploadedFile|array|null $file;
    public string $path = '';
    public string $filePath = '';

    public function __construct()
    {
        $this->file = r()->file('file');
        $day = Carbon::now()->day;
        $month = Carbon::now()->month;

        $mediaType = match ($this->file->extension()) {

            'webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv',
            'mp4', 'm4p', 'ogg', 'm4v', 'avi', 'wmv',
            'mov', 'qt', 'flv', 'swf', 'avchd' => 'video-post',

            default => abort(422, 'unhandled file extension')
        };

        $this->path = "uploads/looms/$month/$day";
    }

    public function fileWithTheSameNameExists()
    {
        return Loom::where('original_name', $this->file->getClientOriginalName())->exists();
    }

    public function storeFileOnServer(): void
    {
        $this->filePath = $this->file->store($this->path, 'public');
    }

    public function fileExists()
    {
        return Storage::disk('public')->exists($this->filePath);
    }

    public function fileNotExists()
    {
        return !$this->fileExists();
    }

    public function deleteFile()
    {
        return Storage::disk('public')->delete($this->filePath);
    }
}
