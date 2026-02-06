import os
from time import sleep
import random
import string
import pytz
from datetime import datetime, timedelta

import numpy as np
from skimage import io, util, transform, exposure
from pathlib import Path
from PIL import Image
import os
from random import randint
from dotenv import load_dotenv
import requests


def pause(_min, _max):
    sleep(randint(_min, _max))


def generate_random_folder():
    tmp = os.path.join('tmp_folder', generate_random_word(20))
    os.makedirs(tmp, exist_ok=True)

    return tmp


def get_post_url(template_path):
    load_dotenv()
    server_url = os.getenv('SERVER_URL')

    return f"{server_url}/storage/{template_path}"


def download_image(image_url, download_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        with open(download_path, 'wb') as f:
            f.write(response.content)
        return download_path
    else:
        raise Exception(f"Failed to download resource from {image_url}. Status code: {response.status_code}")


def process_image(image_path, output_dir):
    image_name = f'{generate_random_word(10)}.jpg'

    # Load the image using skimage
    image = io.imread(image_path)

    # Apply Gaussian noise
    # noisy_image = util.random_noise(image, mode='gaussian', var=0.01)

    # Apply a slight rotation
    rotated_image = transform.rotate(image, angle=randint(1, 2), mode='wrap')

    # Adjust brightness and contrast
    adjusted_image = exposure.adjust_gamma(rotated_image, gamma=0.9)

    # Convert the image to uint8 (8-bit unsigned integer)
    adjusted_image_uint8 = (adjusted_image * 255).astype(np.uint8)

    # Save the image temporarily within the temp directory
    temp_path = os.path.join(output_dir, 'temp_image.png')
    io.imsave(temp_path, adjusted_image_uint8)

    # Open the image with PIL to handle RGBA to RGB conversion
    output_path = os.path.join(output_dir, image_name)

    with Image.open(temp_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Save the final image as JPEG
        img.save(output_path)

    # Clean up the temporary image
    os.remove(temp_path)

    return output_path


def chat_ai(prompt, max_tokens=400, temperature=0.7, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    from openai import OpenAI

    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_SECRET_KEY'))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty)

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(e)


def generate_random_word(length=14):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def get_proxy_details(proxy_ip):
    try:
        response = requests.get(f'http://ipinfo.io/{proxy_ip}/json')
        data = response.json()

        # Extract geolocation (latitude, longitude)
        loc = data.get('loc')

        if loc:
            loc_split = loc.split(',')
            if len(loc_split) == 2:
                latitude = float(loc_split[0])
                longitude = float(loc_split[1])
            else:
                raise ValueError(f"Invalid 'loc' format: {loc}")
        else:
            raise ValueError("'loc' not found in response")

        # Extract timezone and country if available
        timezone = data.get('timezone', 'America/Los_Angeles')  # Default to Los Angeles if not available
        country = data.get('country', 'US')  # Default to US if country info isn't available

        # Default language based on country (you can customize this mapping as needed)
        language_mapping = {
            'US': 'en',
            'FR': 'fr',
            'DE': 'de',
        }

        # Set the language based on the country (default to 'en' for unknown countries)
        language = language_mapping.get(country, 'en')

        # Construct the locale (e.g., en-US, fr-FR)
        locale = f"{language.lower()}-{country.upper()}"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "locale": locale
        }

    except Exception as e:
        print(f"Error fetching proxy details: {e}")

        # Use default values in case of an error
        return {
            "latitude": 0.0,  # Or use an appropriate default
            "longitude": 0.0,  # Or use an appropriate default
            "timezone": 'America/Los_Angeles',  # Default timezone
            "locale": 'en-US'  # Default locale
        }


def get_random_user_agent():
    import random

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.59 Safari/537.36",
    ]

    return random.choice(user_agents)


def tehran_now():
    tehran_tz = pytz.timezone('Asia/Tehran')

    return datetime.now(tehran_tz).replace(tzinfo=None)


def hours_ago(hours):
    return tehran_now() - timedelta(hours=hours)


def hours_later(hours):
    return tehran_now() + timedelta(hours=hours)


def calculate_daily_dms(account_age):
    """
    Calculate the allowed number of DMs an account can send based on its age,
    with randomness for more natural behavior.

    :param account_age: The age of the account in days (integer).
    :return: Allowed number of daily DMs (integer).
    """

    if account_age <= 4:
        return 0
    #
    # if account_age <= 6:
    #     return 0
    #
    # return random.randint(1, 3)
    #
    # if account_age <= 10:
    #     return random.randint(1, 3)
    #
    # if account_age <= 15:
    #     return random.randint(3, 5)

    return random.randint(7, 9)

    if account_age <= 15:
        return random.randint(6, 10)

    return random.randint(6, 10)

    if account_age <= 20:
        return random.randint(10, 15)

    if account_age <= 25:
        return random.randint(15, 22)

    if account_age <= 30:
        return random.randint(22, 27)

    if account_age <= 45:
        return random.randint(27, 30)

    if account_age <= 60:
        return random.randint(28, 33)

    return random.randint(29, 34)


def get_dm_chunk(account_age):
    if account_age <= 6:
        return 0

    # return random.randint(7, 9)
    return random.randint(6, 8)

    if account_age <= 10:
        return random.randint(3, 4)

    if account_age <= 15:
        return random.randint(3, 5)

    if account_age <= 20:
        return random.randint(4, 6)

    if account_age <= 25:
        return random.randint(5, 7)

    if account_age <= 30:
        return random.randint(7, 9)

    if account_age <= 45:
        return random.randint(7, 10)

    if account_age <= 60:
        return random.randint(9, 12)

    return random.randint(9, 12)


def go_to_page(ig, target, name):
    max_retries = 5

    for attempt in range(max_retries):

        try:
            ig.page.goto(target, timeout=50000, wait_until="domcontentloaded")
            ig.account.add_cli(f"{name} page loaded")
            return True

        except Exception as e:
            ig.account.add_cli(f"Attempt {attempt + 1} failed for loading the page : {name}")

        ig.pause(5000, 7000)

    raise Exception(f"Failed to reach {name} after 5 attempts.")


def get_profile_picture():
    from uuid import uuid4

    url = 'https://picsum.photos/500/500'

    headers = {'User-Agent': 'Mozilla/5.0'}

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    filename = f'profile_pictures/image_{uuid4().hex}.jpg'
    with open(filename, 'wb') as f:
        f.write(resp.content)

    print('saved:', filename)

    return filename


def generate_username():
    first_names = [
        "Ethan", "Mason", "Logan", "James", "Benjamin", "Elijah", "Alexander", "Henry", "Jackson", "Sebastian",
        "Aiden", "Matthew", "Samuel", "David", "Joseph", "Carter", "Owen", "Wyatt", "John", "Jack",
        "Luke", "Dylan", "Gabriel", "Isaac", "Nathan", "Julian", "Levi", "Ryan", "Connor", "Christian",
        "Andrew", "Jonathan", "Adrian", "Leo", "Elias", "Anthony", "Joshua", "Daniel", "Aaron", "Evan",
        "Sofia", "Alice", "Victoria", "Gabriela", "Isadora", "Helena", "Beatriz", "Clarissa", "Leticia", "Renata",
        "Carolina", "Fernanda", "Tatiana", "Camilla", "Bianca", "Larissa", "Isabel", "Manuela", "Ana", "Paula",
        "Laura", "Marina", "Valentina", "Bruna", "Yasmin", "Amanda", "Nicole", "Julia", "Carla", "Raquel",
        "Vanessa", "Camile", "Lorena", "Aline", "Isis", "Rafaela", "Júlia", "Gabrielle", "Melissa", "Luana",
        "Evelyn", "Stella", "Clara", "Emilly", "Mirella", "Lara", "Luna", "Victoria", "Sara", "Amanda",
        "Thais", "Isabela", "Marina", "Júlia", "Helena", "Nicole", "Camila", "Sabrina", "Larissa", "Manuela"
    ]

    last_names = [
        "Taylor", "Anderson", "Thomas", "Moore", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia",
        "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young",
        "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson",
        "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards",
        "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy",
        "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray",
        "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes",
        "Ross", "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores",
        "Washington", "Butler", "Simmons", "Foster", "Gonzalez", "Bryant", "Alexander", "Russell", "Griffin", "Diaz",
        "Mendoza", "Freitas", "Souza", "Moreira", "Nascimento", "Alves", "Lima", "Vieira", "Gomes", "Barbosa",
        "Pinto", "Moura", "Fonseca", "Machado", "Cardoso", "Araujo", "Teixeira", "Ramos", "Campos", "Santana"
    ]

    adjectives = [
        "lit", "dope", "epic", "savage", "vibe", "chill", "fresh", "rad", "hype", "wild",
        "crazy", "boss", "swag", "sneaky", "slick", "icy", "flashy", "crisp", "glow", "prime",
        "raw", "urban", "neon", "shady", "stormy", "frosty", "blaze", "fierce", "sleek", "sharp",
        "wavy", "atomic", "cosmic", "pixel", "retro", "drip", "boost", "boosted", "legend", "mythic",
        "hyper", "nova", "galaxy", "vortex", "chaos", "thunder", "storm", "shadow", "ghost", "phantom",
        "viper", "rebel", "blade", "ace", "titan", "quake", "drift", "flare", "ignite", "pulse",
        "strike", "volt", "racer", "crash", "flash", "neo", "cyber", "tech", "steel", "dark",
        "ghostly", "glitch", "crimson", "onyx", "steel", "frost", "ember", "iron", "quantum", "blitz",
        "fusion", "gravity", "omega", "alpha", "beta", "delta", "zen", "echo", "alpha", "drone", "pixelated",
        "hyperdrive", "vivid", "chrome", "neptune", "mars", "apollo", "saturn", "asteroid", "lunar", "solar"
    ]

    first = random.choice(first_names)
    last = random.choice(last_names)
    adj = random.choice(adjectives) if random.random() < 0.5 else ""

    # اضافه کردن شماره تصادفی
    number = str(random.randint(1, 9999)) if random.random() < 0.5 else ""  # 70٪ شانس عدد

    # انتخاب جداکننده تصادفی
    separator = random.choice(["", "_", "__", "._", "_.", "_._", "_.__", "_.__"])

    # ساختار یوزرنیم با طول تصادفی
    username = first + adj + separator + last + number

    # کوتاه یا بلند کردن با اضافه کردن یک جداکننده یا عدد در صورت نیاز
    if len(username) < 10:
        username += str(random.randint(10, 99))
    if len(username) > 28:
        username = username[:28]  # محدودیت اینستاگرام

    return username


def add_cli(log, account):
    from script.models.Cli import Cli

    log = f'[{account.username} -- {account.id}] ${log}'

    print(log)

    # if print_only:
    return False

    truncated_log = (log[:254]) if log else ''

    Cli.create(account_id=account.id, log=truncated_log)
