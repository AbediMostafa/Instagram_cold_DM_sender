<?php

namespace Database\Seeders;

use App\Models\Setting;
use Illuminate\Database\Seeder;

class SettingSeeder extends Seeder
{
    /**
     * Default system settings
     * Unique key: category + key
     */
    private array $settings = [
        // ===== Follow =====
        [
            'type' => 'number',
            'category' => 'Follow',
            'key' => 'Max Follow',
            'value' => '50',
            'description' => 'The maximum follow that an account can perform',
        ],
        [
            'type' => 'number',
            'category' => 'Follow',
            'key' => 'Follow Chunk',
            'value' => '5',
            'description' => 'The selected chunk of usernames to follow every time',
        ],

        // ===== DM =====
        [
            'type' => 'number',
            'category' => 'DM',
            'key' => 'Max DM',
            'value' => '50',
            'description' => 'The maximum dm that an account can perform',
        ],
        [
            'type' => 'number',
            'category' => 'DM',
            'key' => 'DM Chunk',
            'value' => '5',
            'description' => 'The selected chunk of usernames to send dm every time',
        ],
        [
            'type' => 'number',
            'category' => 'DM',
            'key' => 'DM Follow Up Chunk',
            'value' => '5',
            'description' => 'The selected chunk of usernames to follow up every time',
        ],
        [
            'type' => 'text',
            'category' => 'DM',
            'key' => 'cold dm spintax',
            'value' => "👋 {Hey|Hello|Hi} there! {Had|Saw|Noticed} your page {pop up|appear|show up} on my feed and I was {very|really} impressed by your products. {Wanted|Just wanted} to reach out personally because I think you've got {amazing|incredible|outstanding} potential to scale {big|huge|significantly} on TikTok. 🤩 Right now in 2024 there's a {massive|huge|tremendous} opportunity on there with UGC. It's the world's best source of low cost, high quality, and high converting traffic. I've helped brands like yours {boost|improve|skyrocket} their sales by 20k, 30k, even 50k in just 30 days through TikTok UGC—making it *unfairly easy* to do that 😋 I filmed a personalized loom {going over|reviewing|analyzing} your store and why I think you guys in particular would do so well on {that platform|TikTok}. Would you like me to send it your way? {Best|Cheers}, {Edward|E}",
            'description' => 'Spintax template for Cold dm text',
        ],
        [
            'type' => 'text',
            'category' => 'DM',
            'key' => 'first dm follow up spintax',
            'value' => "{ {Hey guys|Hello there}, {just following up|just checking in}. {Did you see|Have you seen} my {message|previous message}? | {Just wanted to|Just checking in to|Reaching out again to} {check in|follow up} again and see if you {had a chance|managed} to {take a look at|review} my previous message about {using|leveraging} TikTok UGC ads to {boost|enhance} your revenue. I {think|believe} this could be a {game-changer|major benefit} for your ecommerce store. {I'd love to|Keen to} chat more about it if you are {interested|keen}. | {Hey guys|Hello again}, I know your inbox is {probably|likely} flooded, but I {wanted to|needed to} make sure my message {didn't get lost|wasn't overlooked} in the shuffle. I {think|believe} the video I recorded for you about {using|implementing} TikTok UGC ads could {really benefit|significantly help} your business. {I'd love to|I'm eager to} send it over to the {owner of|person managing} your brand. {You think|Do you reckon} they'd be interested? | {Hey|Hello again}, {following up|checking in} again because I {think|believe} our approach to TikTok ads could be a {game-changer|major asset} for your business. We've {seen impressive|observed remarkable} results with our clients—I just {posted|shared} up a new case study on my profile—and I'd love to {walk you through|explain} our process. Let me know if I can send the {vid|video} over. | {Hey guys|Hello again}, {wanted to|just checking in to} touch base again and see if you had any questions about our {value-packed|informative} loom on using TikTok UGC ads. It's a {great|fantastic} way to {boost|increase} revenue quickly, and I {think|believe} it could be a {perfect|great} fit for your brand. Just {show|present} the first message I sent to your brand owner if you're a CS rep monitoring this inbox and {let me know|lmk} what they say. | {Hi guys|Hello there}, I {hope you're|trust you are} doing well. I {wanted to|needed to} circle back and see if you {had a chance|got a moment} to review my previous message about {using|implementing} TikTok UGC ads to {increase|boost} revenue. Our approach is {unique|distinct}, and I'm {confident|sure} it could {benefit|help} your business. Let me know if {you're interested|you'd like} and I'll send over a video I made {just for you|specifically for your brand} on how you can scale your brand big on the {fastest growing|most rapidly expanding} social network of 2023 😊 }",
            'description' => 'Spintax template for first follow up message',
        ],
        [
            'type' => 'text',
            'category' => 'DM',
            'key' => 'second dm follow up spintax',
            'value' => "{ {Hey|Hello}. Just wanted to {slide into your DMs|drop a message} again and see if you {had a chance|got the opportunity} to check out our TikTok UGC ad strategy. {We're talking|It's about} quick cash and big gains, so let me know if {you're ready|you're set} to get your ecommerce store {poppin|thriving}. | {Yo|Hey there}, hope {you're killin it|you're doing great}. Just wanted to give you a {friendly reminder|nudge} about that video I {recorded|made} for you showing our TikTok UGC ad approach. It's {low effort, high reward|easy to implement, yet highly effective}, and {perfect|ideal} for savvy brand owners looking to {hit it big|make a mark} this year on a new platform. Unlimited growth. Just {lmk|let me know} if you guys are interested and I'll send it over. | Just wanted to {send a quick message|reach out quickly} and see if you're {ready|prepared} to unlock the {full potential|true power} of TikTok UGC ads. We're talking {extra cheddar|significant earnings} and {serious|major} clout, so {let me know|get in touch} if you're {interested in|keen on} learning more. | Hey {sup|there}, hope you're {crushing it|doing great} in the ecommerce game. Just wanted to remind you about that video I {made|created} for you. It's a {wholly unique|totally different} approach to TikTok UGC ads. {A real game-changer|Incredibly effective}, and I'm {confident|sure} it could take your store to the {next level|top}. Just {tell me|let me know} who to send it to and I'll {email|send} it over :D | Okay okay I know these are getting annoying… But I'm persistent. just wanted to {hit you up|reach out} and see if you're ready to {level up|elevate} your ecommerce game. Our TikTok UGC ad strategy is {low effort, high reward|easy yet effective}, and perfect for {hustlers|go-getters} like you. Let me know if you're {interested in|keen on} learning more and I'll send over the vid I {recorded|made} for you guys. | Just wanted to {touch base|check in} and see if you're {interested in|keen on} exploring this {unique|new} revenue stream to generate an {extra 50k MRR|additional significant monthly recurring revenue} for your ecommerce store? }",
            'description' => 'Spintax template for second follow up message',
        ],
        [
            'type' => 'text',
            'category' => 'DM',
            'key' => 'third dm follow up spintax',
            'value' => "{ Hey hey, hope you're {doing well|in good spirits}. Just wanted to {drop a friendly reminder|remind you} about the vid I {recorded|made} you showing our approach to TikTok UGC ads, and how it would work for your brand in particular. It's a {low-effort, unique and powerful|simple yet potent} way to drive sales and generate buzz for your ecommerce store. Let's chat and see if it's the {right fit|perfect match} for your business. | just wanted to {check in|follow up} and see if you {had a chance to see|managed to review} my previous messages. I made a vid for you showing how you can {exploit|leverage} TikTok UGC ads to add an {extra 50k in MRR|additional significant monthly revenue} to your business in just 30 days. I {really highly|strongly} recommend {taking a few minutes to watch|checking it out}. It could be the key to unlocking {serious|significant} revenue growth for your ecommerce store. If it's a CS rep monitoring this inbox, just {show|present} the store owner my message and {tell me|let me know} if they want me to send it over :D | Okay, this is getting a bit obnoxious by me, but I really don't want you guys to miss out. I just {dropped|published} a huge case study on my profile showing how we took a brand from 0 to 100k months in just 45 days using our proven UGC ads strategy. Since you're an existing brand, with a proven product, we can take yours much higher. {Lmk|Let me know} if you're interested, and I'll send over the loom I filmed you showing exactly how we'd do it for your store. | Last message from me, haha. Just a {reminder|heads-up} about the video I made you. Don't want your brand to miss out on this {huge opportunity|massive chance} to scale on TikTok – it's basically arbitrage compared to the CPMs Facebook and the more established platforms are giving you. {Huge, huge opportunity|Incredible potential}. Just let me know if you or your brand owner or some decision maker wants to see what I put together, and I'll be happy to send it over {right away|immediately} 😊 }",
            'description' => 'Spintax template for third follow up message',
        ],

        // ===== Proxy =====
        [
            'type' => 'number',
            'category' => 'Proxy',
            'key' => 'Max Account For One Proxy',
            'value' => '4',
            'description' => 'The maximum account used for one proxy',
        ],
        [
            'type' => 'text',
            'category' => 'Proxy',
            'key' => 'proxy_type',
            'value' => 'datacenter',
            'description' => 'Default proxy type to use',
        ],

        // ===== Like =====
        [
            'type' => 'number',
            'category' => 'Like',
            'key' => 'Max Like',
            'value' => '200',
            'description' => 'The maximum like that an account can perform',
        ],
        [
            'type' => 'number',
            'category' => 'Like',
            'key' => 'Like Chunk',
            'value' => '3',
            'description' => 'The selected chunk of posts to like every time',
        ],

        // ===== Comment =====
        [
            'type' => 'number',
            'category' => 'Comment',
            'key' => 'Max Comment',
            'value' => '50',
            'description' => 'The maximum comment that an account can perform',
        ],
        [
            'type' => 'number',
            'category' => 'Comment',
            'key' => 'Comment Chunk',
            'value' => '3',
            'description' => 'The selected chunk of posts to comment every time',
        ],
        [
            'type' => 'switch',
            'category' => 'Comment',
            'key' => 'can_like_and_comment',
            'value' => '1',
            'description' => 'Can like and comment simultaneously',
        ],
        [
            'type' => 'number',
            'category' => 'Comment',
            'key' => 'allowed_liking_and_commenting_age',
            'value' => '10',
            'description' => 'Minimum account age for liking and commenting',
        ],

        // ===== Account =====
        [
            'type' => 'number',
            'category' => 'Account',
            'key' => 'Account intervals',
            'value' => '3',
            'description' => "The time (in hours) of each account's interval",
        ],
        [
            'type' => 'number',
            'category' => 'Account',
            'key' => 'Minimum time for next login',
            'value' => '1',
            'description' => 'Specifies the minimum duration (in hours) that must elapse before an account is allowed to log in again after their last login attempt',
        ],
        [
            'type' => 'number',
            'category' => 'Account',
            'key' => 'Maximum time for next login',
            'value' => '3',
            'description' => 'Specifies the maximum duration (in hours) that must elapse before an account is allowed to log in again after their last login attempt',
        ],

        // ===== Templates =====
        [
            'type' => 'switch',
            'category' => 'Templates',
            'key' => 'can_change_name_username',
            'value' => '0',
            'description' => 'Can change both name and username',
        ],
        [
            'type' => 'switch',
            'category' => 'Templates',
            'key' => 'can_check_system_username_with_ig_username',
            'value' => '0',
            'description' => 'Can check if the account logged in with its username and password',
        ],
        [
            'type' => 'number',
            'category' => 'Templates',
            'key' => 'allowed_changing_name_and_username_age',
            'value' => '2',
            'description' => 'Minimum account age for changing name and username',
        ],
        [
            'type' => 'number',
            'category' => 'Templates',
            'key' => 'allowed_changing_avatar_age',
            'value' => '0',
            'description' => 'Minimum account age for changing avatar',
        ],

        // ===== Post =====
        [
            'type' => 'text',
            'category' => 'Post',
            'key' => 'allowed_posting_age',
            'value' => '1',
            'description' => 'Minimum account age for posting',
        ],
        [
            'type' => 'number',
            'category' => 'Post',
            'key' => 'save_post_batch_size',
            'value' => '5',
            'description' => 'Number of different orders to process per account in save_post',
        ],
        [
            'type' => 'number',
            'category' => 'Post',
            'key' => 'comment_batch_size',
            'value' => '3',
            'description' => 'Number of different orders to process per account in comment',
        ],
        [
            'type' => 'text',
            'category' => 'Post',
            'key' => 'order_prepare_batch_size',
            'value' => '3',
            'description' => 'Batch size for preparing orders (view_story, save_post)',
        ],
        [
            'type' => 'text',
            'category' => 'Post',
            'key' => 'view_story_batch_size',
            'value' => '8',
            'description' => 'Batch size for viewing stories',
        ],

        // ===== Mobile =====
        // NOTE: run() deletes any DB setting missing from this seeder, so
        // every mobile_* key the DuoPlus workers read MUST be listed here.
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_stuck_timeout_seconds',
            'value' => '900',
            'description' => 'Seconds before a processing mobile with a stale heartbeat is reset',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_explore_min_posts',
            'value' => '7',
            'description' => 'Minimum posts to view per Explore browse',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_explore_max_posts',
            'value' => '12',
            'description' => 'Maximum posts to view per Explore browse',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_explore_like_chance',
            'value' => '0.2',
            'description' => 'Probability (0-1) of liking each viewed Explore post',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_explore_min_dwell',
            'value' => '8',
            'description' => 'Minimum seconds to dwell on each Explore post',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_explore_max_dwell',
            'value' => '20',
            'description' => 'Maximum seconds to dwell on each Explore post',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_share_seconds',
            'value' => '300',
            'description' => 'Per-account time window (seconds) for the share execution module',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_share_prepare_batch',
            'value' => '3',
            'description' => 'How many share orders one prepare session claims',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_share_stuck_timeout',
            'value' => '120',
            'description' => 'Seconds before a share order stuck in is_prepared=1 is reset to 0',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_share_groups_per_send',
            'value' => '20',
            'description' => 'Maximum share groups ticked in one send',
        ],
        [
            'type' => 'number',
            'category' => 'Mobile',
            'key' => 'mobile_share_per_group',
            'value' => '245',
            'description' => 'Real views sent per group in a send (group member count); customer count is capped at the order total',
        ],

        // ===== General =====
        [
            'type' => 'text',
            'category' => 'General',
            'key' => 'project_path',
            'value' => 'C:\Users\admin\Desktop\project',
            'description' => 'Project root path',
        ],
        [
            'type' => 'text',
            'category' => 'General',
            'key' => 'critical_only_mode',
            'value' => '0',
            'description' => 'Enable critical only mode for automation',
        ],
        [
            'type' => 'text',
            'category' => 'Post',
            'key' => 'can_send_post_from_folder',
            'value' => '1',
            'description' => 'Send post from folder automatically',
        ],
    ];

    /**
     * Run the database seeds.
     * Sync settings: Insert new, Update existing, Delete removed
     */
    public function run(): void
    {
        $seederKeys = collect($this->settings)->map(function ($setting) {
            return $this->makeKey($setting['category'], $setting['key']);
        })->toArray();

        // Get existing settings from DB
        $existingSettings = Setting::all()->keyBy(function ($setting) {
            return $this->makeKey($setting->category, $setting->key);
        });

        $inserted = 0;
        $updated = 0;
        $deleted = 0;

        // Insert or Update
        foreach ($this->settings as $setting) {
            $key = $this->makeKey($setting['category'], $setting['key']);

            if ($existingSettings->has($key)) {
                // Update if changed (but preserve user-modified value)
                $existing = $existingSettings->get($key);

                // Only update type and description, NOT value (user might have changed it)
                if ($existing->type !== $setting['type'] || $existing->description !== $setting['description']) {
                    $existing->update([
                        'type' => $setting['type'],
                        'description' => $setting['description'],
                    ]);
                    $updated++;
                }
            } else {
                // Insert new
                Setting::create($setting);
                $inserted++;
            }
        }

        // Delete removed settings
        foreach ($existingSettings as $key => $existing) {
            if (!in_array($key, $seederKeys)) {
                $existing->delete();
                $deleted++;
            }
        }

        $this->command->info("Settings synced: {$inserted} inserted, {$updated} updated, {$deleted} deleted");
    }

    /**
     * Create unique key from category and key
     */
    private function makeKey(?string $category, string $key): string
    {
        return ($category ?? '') . '::' . $key;
    }
}
