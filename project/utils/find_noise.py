import cv2
import glob
import os
import shutil
import numpy as np


def noise_score(img):
    """
    Estimate image noise using high-frequency residual.
    Higher = noisier.
    """
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    residual = img.astype(np.float32) - blur.astype(np.float32)
    return residual.std()


def compute_noise_threshold(image_dir, multiplier=1.25):
    """
    Compute dataset-based noise threshold.
    """
    images = glob.glob(os.path.join(image_dir, "*.jpg"))
    if not images:
        raise ValueError("No images found!")

    scores = []

    for path in images:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        scores.append(noise_score(img))

    scores = np.array(scores)
    avg = scores.mean()
    threshold = avg * multiplier

    print(f"Average noise score: {avg:.2f}")
    print(f"Noise threshold   : {threshold:.2f}")

    return threshold, avg, scores.tolist()


def remove_noisy_images(image_dir, out_dir, threshold):
    """
    Move images with excessive noise into out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    images = glob.glob(os.path.join(image_dir, "*.jpg"))

    noisy = clean = 0
    print(f"🔍 Checking noise levels for {len(images)} images...\n")

    for path in images:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        score = noise_score(img)
        fname = os.path.basename(path)

        if score > threshold:
            shutil.move(path, os.path.join(out_dir, fname))
            noisy += 1
            print(f"[NOISY] {fname:20s} score={score:.2f}")
        else:
            clean += 1
            print(f"[CLEAN] {fname:20s} score={score:.2f}")

    print("\n📦 Summary:")
    print(f"  Noisy removed: {noisy}")
    print(f"  Clean kept  : {clean}")

    return noisy, clean
