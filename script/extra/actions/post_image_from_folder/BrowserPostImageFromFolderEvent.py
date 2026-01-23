from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.helper import *
import shutil
import random
from script.extra.helper import go_to_page
import urllib3
from script.models.Setting import Setting

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

hashtags_list = [
    'instagram', 'instagood', 'explorepage', 'explore', 'viral', 'trending', 'reels',
    'reelsinstagram', 'reelsvideo', 'fyp', 'motivation', 'inspirational', 'quotes',
    'quoteoftheday', 'success', 'mindset', 'lifestyle', 'entrepreneur', 'business',
    'instadaily', 'instamood', 'follow', 'followme', 'like', 'likeforlikes', 'love',
    'photooftheday', 'instaquote', 'motivationdaily', 'fitnessmotivation', 'selfcare',
    'positivity', 'inspiration', 'goals', 'dreams', 'hardwork', 'nevergiveup',
    'successmindset', 'believe', 'entrepreneurmindset', 'viralreels', 'dailyquotes',
    'attitude', 'wisdom', 'mindsetmatters', 'growthmindset', 'focus', 'hustle',
    'ambition', 'dreambig', 'instareels', 'trendingnow', 'instafamous',
    'positivemindset', 'discipline', 'achiever', 'quote', 'motivationalquote',
    'deepquotes', 'happy', 'inspirationalquotes', 'mindsetcoach', 'selflove', 'vision',
    'lifegoals', 'keepgoing', 'dailyinspiration', 'justdoit', 'lifestyleblogger',
    'exploremore', 'successquotes', 'lifequotes', 'motivationoftheday', 'bestquotes',
    'instagramreels', 'model', 'artistic', 'creativelife', 'motivation101', 'bigdreams',
    'smartwork', 'quotesgram', 'inspirationdaily', 'instaphoto', 'influence',
    'instathoughts', 'epic', 'motivationalpost', 'powerfulquotes', 'entrepreneurlife',
    'businessowner', 'mindsetshift'
]
motivational_sentences = [
    "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "Don’t watch the clock; do what it does. Keep going and make every moment count.",
    "You are never too old to set another goal or to dream a new dream, so start today without hesitation.",
    "It always seems impossible until it’s done, so take the first step and keep moving forward.",
    "The only way to do great work is to love what you do. Passion is the key to excellence.",
    "Hardships often prepare ordinary people for an extraordinary destiny, so embrace every challenge.",
    "The future belongs to those who believe in the beauty of their dreams, so visualize and act.",
    "Do not wait for leaders; do it alone, person to person, and inspire change wherever you go.",
    "Everything you’ve ever wanted is on the other side of fear; courage is the bridge to achievement.",
    "Action is the foundational key to all success, so start acting today and keep improving.",
    "Your limitation—it’s only your imagination; break free and expand your possibilities.",
    "Push yourself, because no one else is going to do it for you; determination is everything.",
    "Great things never come from comfort zones, so challenge yourself and embrace discomfort.",
    "Dream it. Wish it. Do it. Turn your aspirations into actions and your actions into results.",
    "Success doesn’t just find you. You have to go out and get it, working harder every day.",
    "Don’t stop when you’re tired. Stop when you’re done and let your results speak for you.",
    "The harder you work for something, the greater you’ll feel when you achieve it.",
    "Dream bigger. Do bigger. Push beyond your limits and redefine what’s possible for you.",
    "Sometimes we’re tested not to show our weaknesses, but to discover our strengths.",
    "The key to success is to focus on goals, not obstacles, and keep moving forward relentlessly.",
    "Believe you can and you’re halfway there; mindset shapes outcomes more than circumstance.",
    "Don’t wait for the perfect moment. Take the moment and make it perfect with your actions.",
    "Opportunities don’t happen. You create them through persistence, courage, and preparation.",
    "The secret of getting ahead is getting started. Every step forward counts more than you know.",
    "Success is not how high you have climbed, but how you make a positive difference to the world.",
    "Be so good they can’t ignore you. Excellence is recognized when combined with relentless effort.",
    "Your passion is waiting for your courage to catch up. Take the leap and follow your heart.",
    "Work hard in silence, let success make the noise, and focus on your own growth journey.",
    "The only limit to our realization of tomorrow is our doubts of today; act with confidence.",
    "Do what you can, with what you have, where you are, and never underestimate small steps.",
    "Strive for progress, not perfection. Every small improvement compounds into massive results.",
    "Don’t let yesterday take up too much of today. Focus on now and the opportunities ahead.",
    "Set your goals high, and don’t stop until you get there. Ambition fuels extraordinary outcomes.",
    "Success is the sum of small efforts repeated day in and day out; consistency is key.",
    "You don’t have to be perfect to be amazing. Start, improve, and shine along the way.",
    "Failure is not the opposite of success; it’s part of success. Learn and keep moving forward.",
    "The difference between ordinary and extraordinary is that little extra effort every day.",
    "Life is 10% what happens to you and 90% how you react to it; attitude shapes destiny.",
    "Believe in your infinite potential. Your only limitations are those you set upon yourself.",
    "Keep your eyes on the stars and your feet on the ground. Dream big but stay grounded.",
    "Don’t let fear of failure stop you. The greatest achievements are often born from risk.",
    "Small daily improvements over time lead to stunning results; focus on consistency.",
    "Success comes to those who never give up, who learn from mistakes, and keep going forward.",
    "Your time is limited, so don’t waste it living someone else’s life. Follow your own path.",
    "Chase your dreams but always know the road that will lead you home again; balance is key.",
    "The best way to predict your future is to create it. Take charge and design your destiny.",
    "Doubt kills more dreams than failure ever will. Trust yourself and take action fearlessly.",
    "Don’t count the days, make the days count. Every day is an opportunity to get better.",
    "You are capable of amazing things. Believe it, work for it, and never give up.",
    "Life is about making an impact, not making an income. Strive to leave a positive mark.",
    "Success is liking yourself, liking what you do, and liking how you do it. Align passion with work.",
    "Don’t limit your challenges. Challenge your limits and discover what you’re truly capable of.",
    "Great minds discuss ideas; average minds discuss events; small minds discuss people.",
    "The only person you should try to be better than is the person you were yesterday.",
    "Perseverance is failing 19 times and succeeding the 20th. Keep going, you’re almost there.",
    "Your life does not get better by chance, it gets better by change. Take control today.",
    "The harder the battle, the sweeter the victory. Embrace the struggle and grow stronger.",
    "A river cuts through rock not because of its power, but its persistence. Keep flowing.",
    "To succeed, we must first believe that we can. Confidence is the foundation of action.",
    "The man who moves a mountain begins by carrying away small stones; start small, start now.",
    "Don’t be pushed around by the fears in your mind. Be led by the dreams in your heart.",
    "Opportunities multiply as they are seized. Take initiative and doors will open.",
    "Success is not measured by money or status but by the positive impact you create.",
    "Work until your idols become your rivals. Strive for greatness and never settle.",
    "If you want something you’ve never had, you must be willing to do something you’ve never done.",
    "The key to success is to focus our conscious mind on things we desire, not things we fear.",
    "Difficulties in life don’t come to destroy you; they come to help you realize your potential.",
    "Start each day with a positive thought and a grateful heart; mindset drives results.",
    "Be fearless in the pursuit of what sets your soul on fire and your heart full of joy.",
    "You don’t find willpower, you create it. Build habits that lead to unstoppable momentum.",
    "Success is no accident. It is hard work, perseverance, learning, studying, sacrifice, and love of what you do.",
    "Don’t let small minds convince you that your dreams are too big. Think bigger, act bigger.",
    "The pain you feel today will be the strength you feel tomorrow; embrace the challenge.",
    "Life isn’t about waiting for the storm to pass. It’s about learning to dance in the rain.",
    "Be so busy improving yourself that you have no time to criticize others. Focus inward, grow outward.",
    "Act as if what you do makes a difference. It does, more than you know.",
    "You don’t have to see the whole staircase, just take the first step and keep moving.",
    "Hustle in silence and let your success make the noise. Hard work always pays off.",
    "The successful warrior is the average man, with laser-like focus. Concentrate and act.",
    "Don’t let the fear of losing be greater than the excitement of winning. Embrace risk.",
    "In the middle of every difficulty lies opportunity. Look for the lesson and move forward.",
    "A champion is afraid of losing. Everyone else is afraid of winning. Face your fear head-on.",
    "It is never too late to be what you might have been. Take the leap and start now.",
    "Motivation gets you going, but discipline keeps you growing. Build both in daily life.",
    "Success is not for the lazy. Work hard, stay consistent, and your results will show.",
    "Your journey is your own. Don’t compare it with others. Keep moving at your own pace.",
    "Don’t just dream about success; wake up and work hard to make it happen.",
    "Every great achievement was once considered impossible. Start small, dream big.",
    "Life is 10% what happens to you and 90% how you respond to it. Choose wisely.",
    "Your mind is a powerful thing. When you fill it with positive thoughts, your life will start to change.",
    "Discipline is the bridge between goals and accomplishment. Build strong habits daily.",
    "Success isn’t overnight. It’s when every day you get a little better than yesterday.",
    "The best revenge is massive success. Prove them wrong by your results.",
    "Dreams don’t work unless you do. Take action today, no excuses.",
    "You are stronger than you think, braver than you feel, and more capable than you imagine.",
    "The journey of a thousand miles begins with a single step. Start now, keep going.",
    "Don’t wait for opportunity. Create it with hard work, creativity, and persistence.",
    "Some people dream of success, while others wake up and work hard at it. Be the latter.",
    "Your attitude determines your direction. Stay positive, focused, and resilient.",
    "Life rewards action. Take the first step, and momentum will follow.",
    "Success is liking yourself, what you do, and how you do it. Align heart and action.",
    "You can, you should, and if you’re brave enough to start, you will.",
    "When everything seems to be going against you, remember that the airplane takes off against the wind, not with it."
]


class BrowserPostImageFromFolderEvent:
    base = None
    command = 0
    template = None
    image_path = 0
    caption = 0
    tmp = 0

    def __init__(self, ig):
        self.ig = ig
        self.posting_age = int(Setting.get_value("allowed_posting_age"))
        self.can_post = bool(int(Setting.get_value("can_send_post_from_folder")))

    def init(self):

        self.ig.account.add_cli(f"Allowed posting age : {self.posting_age}", print_only=True)
        self.ig.account.add_cli(f"Can post: {self.can_post}", print_only=True)

        if not self.can_post:
            return self.ig.account.add_cli(f"We're not allowed to post")

        if self.ig.account.get_passed_days_since_creation() < self.posting_age:
            return self.ig.account.add_cli(f"Account is not old enough to post image")

        self.ig.account.add_cli(f"Posting an image ...")

        try:
            self.generate_image()
            self.generate_caption()
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem Posting Image : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            if self.tmp:
                shutil.rmtree(self.tmp)
            go_to_page(self.ig, "https://www.instagram.com/", "Home")
            self.ig.pause(3000, 4000)

    def generate_image(self):
        project_path = Setting.get_value('project_path')
        folder_path = fr"{project_path}\script\posts\images"
        files = os.listdir(folder_path)

        random_image = random.choice(files)

        self.ig.account.add_cli('Selected image:', random_image)

        # اگر بخواهی مسیر کامل داشته باشی:
        self.image_path = os.path.join(folder_path, random_image)

    def generate_caption(self):
        quote = random.choice(motivational_sentences)

        selected = random.sample(hashtags_list, random.randint(8, 12))
        hashtags_text = ' '.join([f'#{h}' for h in selected])

        self.caption = f"{quote}\n\n{hashtags_text}"

    def before_change_hook(self):
        self.ig.account.set_state('post image', 'app_state')
        self.command = self.ig.account.create_command('post image', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click()
        except:
            self.ig.page.get_by_role("link", name="New post").click()

        self.ig.pause(3000, 4000)

        try:
            self.ig.page.locator('a[href="#"]:has(svg[aria-label="Post"])').click(timeout=3000)
        except Exception as e:
            try:
                self.ig.account.add_cli(f"Post button doesnt exists : {str(e)}")
                self.ig.page.locator('svg[aria-label="Post"]').click(timeout=3000)
            except Exception as e:
                pass

        self.ig.pause(3000, 3500)

        try:
            self.ig.page.locator(
                "input[accept='image/avif,image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(self.image_path)
        except:
            self.ig.page.locator(
                "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(self.image_path)

        self.ig.pause(3000, 3500)
        try:
            self.ig.page.get_by_role("button", name="OK").click(timeout=3000)
        except:
            pass
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_label("Write a caption...").fill(self.caption)
        self.ig.pause(3000, 4500)

        self.ig.page.get_by_role("button", name="Share").click()

        if self.wait_for_reel_shared():
            self.ig.account.add_cli("Reel shared confirmation received")
        else:
            self.ig.account.add_cli("Reel share confirmation NOT detected")

    def wait_for_reel_shared(self, timeout_sec=70):
        import time

        start = time.time()

        while time.time() - start < timeout_sec:
            try:
                if self.ig.is_visible_by_text('Your reel has been shared') or self.ig.is_visible_by_text(
                        'Your post has been shared'):
                    return True
            except TimeoutError:
                pass

            self.ig.account.add_cli("Post hasn't been posted yet ...")
            time.sleep(5)

        return False

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.add_cli("Image posted successfully")
