import random
import hashlib
import uuid
from instagrapi import Client


class SignupEvent:
    email = None
    password = None
    username = None
    number = None

    def __init__(self, username, password,  email,  number, display_name):
        self.cl = Client()
        self.cl.delay_range = [1, 3]

        self.email = email
        self.password = self.cl.password_encrypt(password)
        self.number = number
        self.username = username
        self.display_name = display_name

    def signup(self):
        proxy_str = f"http://paichb:yNckWHb3@52.128.193.120:29842"
        self.cl.set_proxy(proxy_str)
        self.cl.set_settings({})

        device_settings = self.generate_device_settings_signup()
        print(f"generated device settings : {device_settings}")

        user_agent = self.generate_user_agent_signup(device_settings)
        print(f"generated user agent {user_agent}")

        # Generate consistent device ID
        device_id = self.generate_device_id_signup(device_settings)
        print(f"generated device ID : {device_id}")

        # Generate phone ID
        phone_id = self.generate_phone_id_signup(device_settings)
        print(f"generated phone ID : {phone_id}")

        # Set device settings, including the device ID
        device_settings['device_id'] = device_id
        self.cl.device_id = device_id
        self.cl.phone_id = phone_id

        self.cl.set_device(device_settings)
        self.cl.set_user_agent(user_agent)

        user = self.cl.signup(
            self.username, self.password, self.email, self.number, self.display_name,
            year=random.randint(1970, 2004),
            month=random.randint(1, 12),
            day=random.randint(1, 28)
        )

        return user

    def generate_user_agent_signup(self, device_settings):
        user_agent_template = (
            "Instagram {app_version} Android ({android_version}/{android_release}; "
            "{dpi}; {resolution}; {manufacturer}; {model}; {device}; {cpu}; en_US; {version_code})"
        )
        user_agent = user_agent_template.format(**device_settings)
        return user_agent

    def generate_device_settings_signup(self):
        android_versions = [
            (26, "8.0.0"), (27, "8.1.0"), (28, "9"), (29, "10"), (30, "11"), (31, "12")
        ]
        devices = [
            ("OnePlus", "OnePlus", "6T Dev", "devitron"),
            ("Samsung", "Samsung", "Galaxy S10", "beyond1"),
            ("Google", "Google", "Pixel 4", "flame"),
            ("Xiaomi", "Xiaomi", "Mi 9", "cepheus"),
            ("Huawei", "Huawei", "P30 Pro", "vogue")
        ]
        cpu_types = ["qcom", "exynos", "kirin"]

        android_version, android_release = random.choice(android_versions)
        manufacturer, brand, model, device = random.choice(devices)
        cpu = random.choice(cpu_types)
        dpi = "480dpi"
        resolution = "1080x1920"
        app_version = "269.0.0.18.75"
        version_code = "314665256"

        device_settings = {
            "app_version": app_version,
            "android_version": android_version,
            "android_release": android_release,
            "dpi": dpi,
            "resolution": resolution,
            "manufacturer": manufacturer,
            "device": device,
            "model": model,
            "cpu": cpu,
            "version_code": version_code
        }

        return device_settings

    def generate_device_id_signup(self, device_settings):
        device_info = f"{device_settings['manufacturer']}_{device_settings['model']}_{device_settings['android_version']}"
        hash_object = hashlib.md5(device_info.encode())
        return f"android-{hash_object.hexdigest()[:16]}"

    def generate_phone_id_signup(self, device_settings):
        device_info = f"{device_settings['manufacturer']}_{device_settings['model']}_{device_settings['android_version']}"
        hash_object = hashlib.sha256(device_info.encode())
        return str(uuid.UUID(hash_object.hexdigest()[:32]))


SignupEvent(
    'saram__ough_12',
    'mosthegreate',
    'hiwika2963@owube.com',
    '+17153231146',
        'Hima Shouru'
).signup()
