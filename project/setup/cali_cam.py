import cv2
import os
import shutil
import numpy as np
import sys

# Import project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from model.bundle import build_checkerboard

STREAM_URL = "http://192.168.4.35/high-quality-stream"

BASE_DIR = "../data/CALI"
CAPTURE_DIR = os.path.join(BASE_DIR, "cali_images")
BLURRY_DIR = os.path.join(BASE_DIR, "cali_blurry")
NOISY_DIR = os.path.join(BASE_DIR, "cali_noisy")
BW_DIR = os.path.join(BASE_DIR, "cali_bw")

RESET_FOLDERS = [CAPTURE_DIR, BLURRY_DIR, NOISY_DIR, BW_DIR]

CHECKERBOARD = (9, 6)
MAX_IMAGES = 50

def reset_calibration_folders():
    print("🧹 Resetting calibration folders...")

    for folder in RESET_FOLDERS:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

    print("Calibration directories ready.")


def detect_checkerboard(gray, pattern):
    """Return True, corners if found else False, None."""
    found, corners = cv2.findChessboardCorners(gray, pattern)
    return found, corners


def capture_calibration_images():
    reset_calibration_folders()

    objp = build_checkerboard(CHECKERBOARD)

    print(f"Ready to capture {MAX_IMAGES} calibration images...")
    print("Move the checkerboard into view.")

    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("Cannot open ESP32 stream.")
        return

    saved = 0

    while saved < MAX_IMAGES:
        ret, frame = cap.read()
        if not ret:
            print("⚠ No frame received.")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        found, corners = detect_checkerboard(gray, CHECKERBOARD)

        if found:
            filename = os.path.join(CAPTURE_DIR, f"calib_{saved:02d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            saved += 1

        cv2.imshow("Calibration Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("Calibration capture complete!")


if __name__ == "__main__":
    capture_calibration_images()
