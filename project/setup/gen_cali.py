import cv2
import numpy as np
import glob
import sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

sys.path.append(ROOT_DIR)

from model.calibration_data import save_calibration

# FIX PROJECT ROOT DIRECTORY
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "CALI")

IMAGE_DIR = os.path.join(DATA_DIR, "cali_images", "*.jpg")
CALIB_DIR = os.path.join(DATA_DIR, "calibration")
CALIB_PATH = os.path.join(CALIB_DIR, "calibration_data.npz")

os.makedirs(CALIB_DIR, exist_ok=True)

CHECKERBOARD = (9, 6)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Object points for checkerboard (3D world)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []  # 3D
imgpoints = []  # 2D

# REMOVE OLD CALIBRATION FILE
if os.path.exists(CALIB_PATH):
    os.remove(CALIB_PATH)
    print(f"Removed existing calibration file: {CALIB_PATH}")

# LOAD IMAGES
images = glob.glob(IMAGE_DIR)
print(f"Found {len(images)} calibration images in:\n  {IMAGE_DIR}")

if len(images) == 0:
    print("ERROR: No images found. Run cali_cam.py first.")
    exit()

# PROCESS EACH IMAGE
for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"Could not open: {fname}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
    if found:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        objpoints.append(objp)
        imgpoints.append(corners2)

        print(f"✔ Chessboard detected: {os.path.basename(fname)}")
    else:
        print(f"✖ Chessboard NOT detected: {os.path.basename(fname)}")

# PERFORM CALIBRATION
if objpoints and imgpoints:
    print("\n🔧 Performing camera calibration...")
    
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    save_calibration(
        CALIB_PATH,
        K=mtx,
        dist=dist,
        rvecs=rvecs,
        tvecs=tvecs
    )

    print("\nCalibration SUCCESSFUL!")
    print(f"Saved full calibration (intrinsics + extrinsics) to:\n  {CALIB_PATH}")

else:
    print("\nCalibration failed — no valid chessboard detections.")
