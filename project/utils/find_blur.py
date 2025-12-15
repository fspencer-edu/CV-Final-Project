import cv2
import glob
import os
import shutil


def blur_score(image_path):
    """Return Laplacian variance blur score."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
    return cv2.Laplacian(img, cv2.CV_64F).var()


def remove_blurry_images(image_dir, out_dir, threshold=120.0):
    """Move blurry images (score < threshold) into out_dir."""
    os.makedirs(out_dir, exist_ok=True)

    images = glob.glob(os.path.join(image_dir, "*.jpg"))
    print(f"Checking {len(images)} images...")

    blurry = 0
    sharp = 0

    for path in images:
        score = blur_score(path)
        filename = os.path.basename(path)

        if score < threshold:
            shutil.move(path, os.path.join(out_dir, filename))
            blurry += 1
            print(f"[BLUR]  {filename:20s}  score={score:.2f}")
        else:
            sharp += 1
            print(f"[SHARP] {filename:20s}  score={score:.2f}")

    print(f"\nSummary:")
    print(f"  Blurry: {blurry}")
    print(f"  Sharp:  {sharp}")

    return blurry, sharp
