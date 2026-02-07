#!/usr/bin/env python3
"""
Face Modifier using Google AI Studio - Gemini 2.5 Flash Image (Nano Banana)
FREE - No billing required

Requirements:
    pip install requests Pillow

Get your FREE API key from: https://aistudio.google.com/apikey
"""

import os
import sys
import time
import base64
import shutil
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from io import BytesIO


# Install packages
def install_packages():
    packages = ["requests", "Pillow"]
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


install_packages()

import requests
from PIL import Image

# ============== CONFIGURATION ==============
# Get FREE API key from: https://aistudio.google.com/apikey
API_KEY = "AIzaSyBUvHQZefAZNzF7Ogzetq6TEL3ASKvoUlo"

# Nano Banana - FREE image generation model
# Options: "gemini-2.0-flash-exp" (free) or "gemini-2.5-flash-image" (may need billing)
MODEL_NAME = "gemini-2.0-flash-exp"

# Google AI Studio API endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
DELAY_BETWEEN_REQUESTS = 7  # seconds (rate limit: ~10 RPM)

# Prompt for face replacement
MODIFICATION_PROMPT = """Generate an edited version of this image where you replace the face with a completely different person's face.

IMPORTANT: You must output the modified image.

Keep exactly the same:
- Body pose and position
- Clothing and accessories
- Background and lighting
- Image style and quality
- Camera angle

The new face should:
- Be a realistic, natural-looking different person
- Match the same skin tone and lighting
- Have a similar expression/mood
- Look photorealistic, not AI-generated

Output the generated image."""


def setup_logging(script_dir: Path):
    log_file = script_dir / f"face_modifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    logger = logging.getLogger('face_modifier')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, log_file


def get_script_directory() -> Path:
    return Path(__file__).parent.resolve()


def get_image_files(directory: Path) -> list[Path]:
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(directory.glob(f"*{ext}"))
        images.extend(directory.glob(f"*{ext.upper()}"))
    images = [img for img in images if "temp" not in str(img)]
    return sorted(set(images))


def ensure_temp_folder(directory: Path) -> Path:
    temp_folder = directory / "temp"
    temp_folder.mkdir(exist_ok=True)
    return temp_folder


def load_and_prepare_image(image_path: Path) -> tuple[str, tuple[int, int]]:
    img = Image.open(image_path)

    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Upscale small images
    min_size = 512
    if min(img.size) < min_size:
        ratio = min_size / min(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Resize if too large
    max_size = 1024
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return base64_data, img.size


def modify_face(logger, image_path: Path) -> bytes | None:
    try:
        logger.debug(f"Loading image: {image_path}")
        image_base64, img_size = load_and_prepare_image(image_path)
        logger.debug(f"Image size: {img_size}")

        url = f"{API_URL}?key={API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "text": MODIFICATION_PROMPT
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        logger.debug(f"Sending request to Google AI Studio...")

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        logger.debug(f"Response status: {response.status_code}")

        if response.status_code != 200:
            error_msg = response.text[:500]
            logger.error(f"API Error {response.status_code}: {error_msg}")

            if response.status_code == 429:
                logger.warning("Rate limit - waiting 60s...")
                time.sleep(60)

            return None

        result = response.json()
        logger.debug(f"Response keys: {list(result.keys())}")

        # Extract image from response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            content = candidate.get('content', {})
            parts = content.get('parts', [])

            for part in parts:
                # Check for inline image data
                if 'inlineData' in part:
                    inline_data = part['inlineData']
                    if 'data' in inline_data:
                        logger.info("Image extracted successfully")
                        return base64.b64decode(inline_data['data'])

                # Log text parts for debugging
                if 'text' in part:
                    text = part['text'][:300]
                    logger.debug(f"Text response: {text}...")

        logger.warning("No image in response")
        logger.debug(f"Full response: {json.dumps(result, indent=2, default=str)[:2000]}")
        return None

    except requests.exceptions.Timeout:
        logger.error("Request timeout (180s)")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def process_images():
    script_dir = get_script_directory()
    logger, log_file = setup_logging(script_dir)

    logger.info("")
    logger.info("=" * 55)
    logger.info("  Face Modifier - Google AI Studio (FREE)")
    logger.info("  Model: Nano Banana (Gemini 2.5 Flash Image)")
    logger.info("=" * 55)
    logger.info(f"[i] Directory: {script_dir}")
    logger.info(f"[i] Log file: {log_file.name}")

    # Check API key
    if API_KEY == "YOUR_API_KEY_HERE":
        logger.error("")
        logger.error("[X] API key not set!")
        logger.info("")
        logger.info("  Get your FREE API key:")
        logger.info("  1. Go to: https://aistudio.google.com/apikey")
        logger.info("  2. Create a new key")
        logger.info("  3. Paste it in this script (line 42)")
        logger.info("")
        return

    temp_folder = ensure_temp_folder(script_dir)
    images = get_image_files(script_dir)

    if not images:
        logger.error("[X] No images found!")
        logger.info(f"    Supported: {', '.join(IMAGE_EXTENSIONS)}")
        return

    logger.info(f"[i] Images found: {len(images)}")
    logger.info(f"[i] Backup folder: {temp_folder}")
    logger.info(f"[i] Delay: {DELAY_BETWEEN_REQUESTS}s")
    logger.info("")
    logger.info("=" * 55)
    logger.info("")

    success_count = 0
    fail_count = 0

    for i, image_path in enumerate(images, 1):
        logger.info(f"[{i}/{len(images)}] Processing: {image_path.name}")

        modified_data = modify_face(logger, image_path)

        if modified_data:
            temp_path = temp_folder / image_path.name
            shutil.move(str(image_path), str(temp_path))
            logger.info(f"  [>] Original -> temp/{image_path.name}")

            output_path = script_dir / image_path.name
            with open(output_path, "wb") as f:
                f.write(modified_data)
            logger.info(f"  [+] Saved: {image_path.name}")

            success_count += 1
        else:
            fail_count += 1
            logger.warning(f"  [-] Skipped")

        if i < len(images):
            logger.info(f"  [...] Waiting {DELAY_BETWEEN_REQUESTS}s...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

        logger.info("")

    logger.info("=" * 55)
    logger.info("[i] Summary:")
    logger.info(f"    Success: {success_count}")
    logger.info(f"    Failed: {fail_count}")
    logger.info(f"    Originals: temp/")
    logger.info(f"    Log: {log_file.name}")
    logger.info("=" * 55)


if __name__ == "__main__":
    process_images()