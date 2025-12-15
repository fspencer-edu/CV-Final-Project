import cv2
import numpy as np
import os
import glob

# PREPROCESSING FUNCTIONS
def gamma_correct(img, gamma=1.2):
    inv = 1.0 / gamma
    table = (np.linspace(0, 1, 256) ** inv) * 255
    table = np.clip(table, 0, 255).astype(np.uint8)
    return cv2.LUT(img, table)

def remove_vignette(img, strength=0.65):
    h, w = img.shape[:2]
    Y, X = np.indices((h, w))
    cx, cy = w / 2, h / 2
    dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
    dist /= dist.max()
    mask = 1 + strength * (dist ** 2)
    corrected = np.zeros_like(img)
    for c in range(3):
        corrected[..., c] = np.clip(img[..., c] * mask, 0, 255)
    return corrected.astype(np.uint8)

def denoise(img):
    return cv2.fastNlMeansDenoisingColored(
        img, None,
        h=8, hColor=8,
        templateWindowSize=7, searchWindowSize=21
    )

def sharpen(img, amount=1.5):
    blur = cv2.GaussianBlur(img, (0, 0), sigmaX=1.2)
    return cv2.addWeighted(img, amount, blur, -(amount - 1), 0)

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def preprocess_bw(img):
    img = gamma_correct(img, gamma=1.25)
    img = remove_vignette(img, strength=0.65)
    img = denoise(img)
    img = sharpen(img, amount=1.6)
    img = to_grayscale(img)
    return img

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "CALI")

INPUT_DIR = os.path.join(DATA_DIR, "cali_images")
OUTPUT_DIR = os.path.join(DATA_DIR, "cali_bw")

os.makedirs(OUTPUT_DIR, exist_ok=True)

image_paths = glob.glob(os.path.join(INPUT_DIR, "*.jpg"))

print(f"Processing {len(image_paths)} images from:\n  {INPUT_DIR}")

for path in image_paths:
    img = cv2.imread(path)
    if img is None:
        print(f"Could not open {path}")
        continue

    bw_img = preprocess_bw(img)
    filename = os.path.basename(path)
    save_path = os.path.join(OUTPUT_DIR, filename)

    cv2.imwrite(save_path, bw_img)
    print(f"Saved BW: {save_path}")

print("\nBatch preprocessing complete!")
