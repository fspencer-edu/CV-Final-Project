"""
bundle.py

Runs post-calibration refinement using:
    - checkerboard.py utilities
    - calibration_data.py I/O
Produces:
    calibration_data_opt.npz
"""

import os
import numpy as np
import cv2
import glob

# Import internal modules
from model.calibration_data import load_calibration, save_calibration
from model.checkerboard import (
    normalize_extrinsics,
    build_checkerboard,
    extract_checkerboard_points,
    compute_world_points
)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR   = os.path.join(ROOT_DIR, "data", "CALI")
CALIB_DIR  = os.path.join(DATA_DIR, "calibration")

CALIB_IN  = os.path.join(CALIB_DIR, "calibration_data.npz")
CALIB_OUT = os.path.join(CALIB_DIR, "calibration_data_opt.npz")

IMAGE_GLOB = os.path.join(DATA_DIR, "cali_images", "*.jpg")


# MAIN BUNDLE ADJUSTMENT PIPELINE
def run_bundle_adjustment():

    print("\n===========================================")
    print("     Bundle Adjustment Pipeline")
    print("===========================================\n")

    # 1. Load initial calibration
    print(f"Loading initial calibration:\n  {CALIB_IN}\n")
    K, dist, rvecs_raw, tvecs_raw = load_calibration(CALIB_IN)

    # 2. Normalize extrinsics
    (
        rvecs,
        tvecs,
        camera_positions,
        rotations
    ) = normalize_extrinsics(rvecs_raw, tvecs_raw)

    print("Initial camera centers:")
    print(camera_positions)

    # 3. Build checkerboard
    CHECKERBOARD = (9, 6)
    square_size  = 2.5

    objp = build_checkerboard(CHECKERBOARD, square_size)

    # 4. Extract corners again (optional)
    print("\nExtracting checkerboard points from images...")
    objpoints, imgpoints = extract_checkerboard_points(
        IMAGE_GLOB, CHECKERBOARD, square_size
    )
    print(f"Found {len(objpoints)} valid images.")

    # 5. Compute world-space point cloud (P)
    print("\nComputing world-space points...")
    P, camera_positions_new, rotations_new = compute_world_points(
        objp, rvecs, tvecs
    )

    print("Updated camera centers:")
    print(camera_positions_new)

    # 6. Run bundle adjustment (placeholder)
    print("\n⚠ [NOTE] Bundle adjustment step not implemented yet.")
    print("    - You can integrate your OpenCV BA refine here.\n")
    
    # For now, we simply keep original calibration
    K_opt = K
    dist_opt = dist
    rvecs_opt = rvecs
    tvecs_opt = tvecs

    # 7. Save updated calibration
    print(f"Saving optimized calibration to:\n  {CALIB_OUT}\n")

    save_calibration(
        CALIB_OUT,
        K=K_opt,
        dist=dist_opt,
        rvecs=rvecs_opt,
        tvecs=tvecs_opt
    )

    print("Bundle-adjusted calibration saved successfully!\n")


# RUN IF CALLED DIRECTLY
if __name__ == "__main__":
    run_bundle_adjustment()
