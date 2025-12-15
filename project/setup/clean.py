import os
import shutil
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.find_blur import remove_blurry_images
from utils.find_noise import compute_noise_threshold, remove_noisy_images


DATA_DIR = os.path.join(ROOT_DIR, "data", "CALI")

IMAGE_DIR     = os.path.join(DATA_DIR, "cali_images")
BLUR_OUT_DIR  = os.path.join(DATA_DIR, "cali_blurry")
NOISE_OUT_DIR = os.path.join(DATA_DIR, "cali_noisy")

for folder in [IMAGE_DIR, BLUR_OUT_DIR, NOISE_OUT_DIR]:
    os.makedirs(folder, exist_ok=True)


def restore_images(src_dir, dest_dir):
    if not os.path.isdir(src_dir):
        return

    restored = 0
    for file in os.listdir(src_dir):
        if file.lower().endswith((".jpg", ".png")):
            shutil.move(os.path.join(src_dir, file),
                        os.path.join(dest_dir, file))
            restored += 1

    if restored > 0:
        print(f"Restored {restored} images from {src_dir} → {dest_dir}")


restore_images(BLUR_OUT_DIR, IMAGE_DIR)
restore_images(NOISE_OUT_DIR, IMAGE_DIR)

print("\nRemoving blurry images...")
remove_blurry_images(IMAGE_DIR, BLUR_OUT_DIR, threshold=120.0)

print("\nCalculating noise threshold...")
threshold, avg, _ = compute_noise_threshold(IMAGE_DIR, multiplier=1.10)
print(f"➡ Noise threshold = {threshold:.2f}")

print("\nRemoving noisy images...")
remove_noisy_images(IMAGE_DIR, NOISE_OUT_DIR, threshold)


print("\nCleaning process complete!")
