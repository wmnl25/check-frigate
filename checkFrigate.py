import requests
import time
from PIL import Image
import imagehash
import io
import os

# Configuration
URL = "http://frigate:5000/api/entree/latest.webp?h=344&cache=1734254308389"
REFERENCE_IMAGE_PATH = "latest.webp"  # Local uploaded image
CHECK_INTERVAL = 5 * 60  # 5 minutes in seconds
RETRY_DELAY = 5  # Retry delay in seconds
RETRY_COUNT = 5  # Number of additional retries if match is found

# Function: Perform the action if condition is met
def perform_action():
    print("[ACTION TRIGGERED] Images match continuously. Performing the action...")
    # Example: Replace with actual code for the action
    os.system("docker restart frigate")

# Function: Download image from a URL
def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch image: {e}")
        return None

# Function: Compare two images using image hashing
def images_match(image1, image2):
    hash1 = imagehash.average_hash(image1)
    hash2 = imagehash.average_hash(image2)
    return hash1 == hash2

# Main Loop
def monitor_images():
    print("[STARTING] Monitoring images...")
    reference_image = Image.open(REFERENCE_IMAGE_PATH)

    while True:
        print("[INFO] Checking image...")
        first_image = download_image(URL)
        if first_image is None:
            print("[WARNING] Could not fetch the first image. Skipping...")
            time.sleep(CHECK_INTERVAL)
            continue

        # Compare with reference image
        if images_match(reference_image, first_image):
            print("[MATCH FOUND] First image matches reference. Retrying...")
            match = True

            # Retry to confirm persistent match
            for i in range(RETRY_COUNT):
                time.sleep(RETRY_DELAY)
                retry_image = download_image(URL)
                if retry_image is None or not images_match(reference_image, retry_image):
                    print(f"[RETRY {i+1}] No match. Condition reset.")
                    match = False
                    break
                print(f"[RETRY {i+1}] Match confirmed.")

            # If all retries match, perform the action
            if match:
                perform_action()
        else:
            print("[INFO] No match found.")

        print(f"[WAITING] Next check in {CHECK_INTERVAL // 60} minutes...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_images()

