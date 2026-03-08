<?php

namespace App\Http\Controllers;

use App\Models\Proxy;
use App\Models\Setting;
use Illuminate\Http\Request;

class SettingController extends Controller
{
    public function index()
    {
        return [
            'proxy_types' => Proxy::select('type')?->distinct()?->pluck('type'),
            'proxy_type' => Setting::getValue('proxy_type'),
            'critical_only_mode' => Setting::getValue('critical_only_mode'),

            // Post from folder
            'can_send_post_from_folder' => Setting::getValue('can_send_post_from_folder'),
            'allowed_posting_age' => Setting::getValue('allowed_posting_age'),

            // Batch sizes
            'save_post_batch_size' => Setting::getValue('save_post_batch_size'),
            'comment_batch_size' => Setting::getValue('comment_batch_size'),
            'story_prepare_batch_size' => Setting::getValue('story_prepare_batch_size'),
            'view_story_batch_size' => Setting::getValue('view_story_batch_size'),
        ];
    }

    public function update()
    {
        return tryCatch(
            function () {
                foreach (r()->all() as $key => $value) {
                    if (is_bool($value)) {
                        $value = $value ? "1" : "0";
                    }
                    Setting::setValue($key, $value);
                }
            },
            'Setting updated successfully'
        );
    }
}
