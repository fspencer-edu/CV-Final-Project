"""
calibration_data.py

This module provides:
    - load_calibration(path)
    - save_calibration(path, K, dist, rvecs, tvecs)

The .npz file must contain:
    camera_matrix : (3,3)
    dist_coeffs   : (N,) distortion coefficients
    rvecs         : list/array of (3,1) rotation vectors
    tvecs         : list/array of (3,1) translation vectors
"""

import os
import numpy as np


def load_calibration(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Calibration file not found: {path}")

    data = np.load(path, allow_pickle=True)

    # Extract and enforce float64 representations
    K = np.asarray(data["camera_matrix"], dtype=np.float64)
    dist = np.asarray(data["dist_coeffs"], dtype=np.float64)

    # Ensure rvecs/tvecs are lists of (3,1) float64 arrays
    rvecs_raw = data["rvecs"]
    tvecs_raw = data["tvecs"]

    rvecs = [np.asarray(r, dtype=np.float64).reshape(3, 1) for r in rvecs_raw]
    tvecs = [np.asarray(t, dtype=np.float64).reshape(3, 1) for t in tvecs_raw]

    return K, dist, rvecs, tvecs


def save_calibration(path, K, dist, rvecs, tvecs):
    # Create folder if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Convert lists to object arrays for NPZ
    rvecs_arr = np.array(rvecs, dtype=object)
    tvecs_arr = np.array(tvecs, dtype=object)

    np.savez(
        path,
        camera_matrix=np.asarray(K, dtype=np.float64),
        dist_coeffs=np.asarray(dist, dtype=np.float64),
        rvecs=rvecs_arr,
        tvecs=tvecs_arr
    )

    print(f"[calibration_data] Saved calibration file → {path}")
