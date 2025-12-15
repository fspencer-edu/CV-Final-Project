"""
bundle.py

Utility functions for:
    - Normalizing extrinsics (rvecs, tvecs)
    - Building checkerboard templates
    - Extracting corner detections from calibration images
    - Computing world-space checkerboard points (P)
    - Computing camera centers and rotations
"""

import numpy as np
import cv2
import glob
import os


# 1. Normalize extrinsics (rvecs, tvecs)
def normalize_extrinsics(rvecs_raw, tvecs_raw):
    rvecs = [np.array(r, dtype=np.float64).reshape(3, 1) for r in rvecs_raw]
    tvecs = [np.array(t, dtype=np.float64).reshape(3, 1) for t in tvecs_raw]

    camera_positions = []
    rotations = []

    for rvec, tvec in zip(rvecs, tvecs):
        R, _ = cv2.Rodrigues(rvec)
        C = -R.T @ tvec.reshape(3)
        camera_positions.append(C)
        rotations.append(R)

    return rvecs, tvecs, np.array(camera_positions), rotations


# 2. Build checkerboard template (objp)
def build_checkerboard(CHECKERBOARD=(9, 6), square_size=2.5):
    cols, rows = CHECKERBOARD
    objp = np.zeros((cols * rows, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    objp[:, :2] *= square_size
    return objp


# 3. Extract objpoints/imgpoints from image directory
def extract_checkerboard_points(image_glob_path, CHECKERBOARD=(9, 6), square_size=2.5):
    objp = build_checkerboard(CHECKERBOARD, square_size)

    objpoints = []
    imgpoints = []

    images = glob.glob(image_glob_path)

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD)

        if found:
            objpoints.append(objp)
            imgpoints.append(corners)

    return objpoints, imgpoints


# 4. Compute P (world-space checkerboard points) + camera poses
def compute_world_points(objp, rvecs, tvecs):
    P = []
    camera_positions = []
    rotations = []

    for rvec, tvec in zip(rvecs, tvecs):
        R, _ = cv2.Rodrigues(rvec)
        C = -R.T @ tvec.reshape(3)

        camera_positions.append(C)
        rotations.append(R)

        pts_world = (R.T @ (objp - tvec.reshape(1, 3)).T).T
        P.append(pts_world)

    return np.vstack(P), np.array(camera_positions), rotations
