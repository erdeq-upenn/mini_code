import os
import time
import random
import requests
from tqdm import tqdm
from urllib.parse import urlparse

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_URL = "https://javtube.com/javpic/manami-sasaki/35/manami-sasaki-"
DOWNLOAD_DIR = "/Users/dequaner/Desktop/Mirror/download_pics/1/manami-sasaki"
MAX_RETRIES = 3
SLEEP_RANGE = (1, 3)
LOG_FILE = "downloaded_images.txt"
MIN_VALID_SIZE = 10 * 1024  # 10 KB

# -----------------------------
# HEADERS & SESSION SETUP
# -----------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    "Referer": "https://javtube.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

session = requests.Session()
session.headers.update(HEADERS)

# -----------------------------
# FUNCTION TO CHECK IF FILE IS VALID
# -----------------------------
def is_image_valid(filepath):
    return os.path.exists(filepath) and os.path.getsize(filepath) >= MIN_VALID_SIZE

# -----------------------------
# FUNCTION TO GENERATE FILENAME FROM URL
# -----------------------------
def get_parsed_filename(img_url):
    path_parts = urlparse(img_url).path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Unexpected URL structure.")
    folder_number = path_parts[-2]
    filename = path_parts[-1]
    return f"{folder_number}-{filename}"

# -----------------------------
# FUNCTION TO GENERATE UNIQUE FILENAME
# -----------------------------
def get_unique_filename(filepath):
    if not os.path.exists(filepath):
        return filepath
    base, ext = os.path.splitext(filepath)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

# -----------------------------
# FUNCTION TO DOWNLOAD IMAGE
# -----------------------------
def download_image(img_number: int):
    img_url = f"{BASE_URL}{img_number}.jpg"
    try:
        filename = get_parsed_filename(img_url)
    except Exception as e:
        print(f"⚠️ Error parsing URL for image {img_number}: {e}")
        return False

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(DOWNLOAD_DIR, filename)

    if is_image_valid(dest_path):
        print(f"🟡 Skipping valid image: {filename}")
        return True

    dest_path = get_unique_filename(dest_path)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(img_url, stream=True, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Attempt {attempt}: Image {img_number} not found (status {response.status_code})")
                time.sleep(1)
                continue

            total_size = int(response.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(
                desc=f"⬇️ Downloading {filename}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                leave=False
            ) as bar:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    bar.update(len(chunk))

            if not is_image_valid(dest_path):
                print(f"❌ Downloaded {filename} but size is too small. Retrying...")
                time.sleep(1)
                continue

            print(f"✅ Saved: {dest_path}")
            return True
        except Exception as e:
            print(f"❌ Attempt {attempt} failed for image {img_number}: {e}")
            time.sleep(1)

    print(f"🚫 Giving up on image {img_number} after {MAX_RETRIES} attempts.")
    return False

# -----------------------------
# FUNCTION TO LOG SUCCESS
# -----------------------------
def log_success(img_number):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{img_number}\n")

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def main():
    try:
        start_number = int(input("Enter the starting image number (e.g., 0): "))
        end_number = int(input("Enter the ending image number (e.g., 20): "))

        print(f"\n🔽 Downloading images {start_number} to {end_number}...\n")

        for img_number in range(start_number, end_number + 1):
            success = download_image(img_number)
            if success:
                log_success(img_number)
            time.sleep(random.uniform(*SLEEP_RANGE))

        print("\n✅ All downloads attempted.")
        print(f"📄 Download log saved to: {LOG_FILE}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
