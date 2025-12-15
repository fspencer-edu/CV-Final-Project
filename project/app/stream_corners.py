import cv2
import numpy as np
import time
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from model.corners import (
    detect_edges,
    filter_lines,
    extend_segment,
    intersect,
    extract_corners_from_points,
    refine_corners_harris,
    draw_corners,
)
from model.calibration_data import load_calibration
from model.hand_gesture import HandGestureController

try:
    from pynput.keyboard import Controller, Key
    keyboard = Controller()
except ImportError:
    keyboard = None
    print("⚠ pynput not installed. Gestures will only be printed, not sent to OS.")

# Hand gesture controller
gesture = HandGestureController()

# CONFIG

STREAM_URL = "http://192.168.4.35/high-quality-stream"
CALIB_PATH = "../data/CALI/calibration/calibration_data_opt.npz"

SMOOTH_ALPHA = 0.25   # temporal smoothing for screen corners


# Temporal smoother

class CornerSmoother:
    def __init__(self, alpha=0.25):
        self.alpha = alpha
        self.prev = None

    def smooth(self, corners):
        """
        corners: list of (x,y) points, e.g. [TL,TR,BR,BL]
        """
        corners = np.array(corners, float)

        if self.prev is None:
            self.prev = corners
            return corners

        smoothed = self.alpha * corners + (1 - self.alpha) * self.prev
        self.prev = smoothed
        return smoothed


from pynput.keyboard import Key
from pynput.mouse import Controller as MouseController

def switch_app(direction):
    """
    direction: 'left' or 'right'
    Performs Cmd+Tab and then Arrow Left/Right while Cmd is still held.
    """

    # Hold ⌘
    keyboard.press(Key.cmd)

    # Switcher opens only when Tab is pressed WHILE Cmd is held
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)

    # VERY IMPORTANT: tiny delay helps macOS register switcher
    time.sleep(0.05)

    # Move left or right inside app switcher
    if direction == "left":
        keyboard.press(Key.left)
        keyboard.release(Key.left)
        print("⬅ Cmd+Tab → Move Left")

    elif direction == "right":
        keyboard.press(Key.right)
        keyboard.release(Key.right)
        print("➡ Cmd+Tab → Move Right")

    # Release ⌘ **AFTER** arrow navigation
    keyboard.release(Key.cmd)

mouse = MouseController()

def handle_gesture(direction):
    print(f"🤚 Gesture detected: {direction}")

    if keyboard is None:
        print("Keyboard unavailable")
        return

    # --- SCROLL UP ---
    if direction == "up":
        for _ in range(10):          # smooth effect
            mouse.scroll(0, 20)

    # --- SCROLL DOWN ---
    elif direction == "down":
        for _ in range(10):
            mouse.scroll(0, -20)

    if direction == "left":
        switch_app("left")
        return

    elif direction == "right":
        switch_app("right")
        return


# MAIN LOOP

def main():

    # Load optimized intrinsics (we don't modify them here, just use them if needed)
    K, dist, *_ = load_calibration(CALIB_PATH)
    K = K.astype(np.float64)
    dist = dist.astype(np.float64)

    smoother = CornerSmoother(alpha=SMOOTH_ALPHA)

    # Open ESP32 stream
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        raise RuntimeError("Cannot open ESP32 stream.")
    
    print("Streaming from:", STREAM_URL)
    print("Press Q to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Failed frame read.")
            time.sleep(0.03)
            continue

        img = frame.copy()

        # STEP 1 — Edge detection
        edges = detect_edges(img)

        # STEP 2 — Hough lines
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=80,
            minLineLength=0.15 * img.shape[1],
            maxLineGap=25
        )

        if lines is None:
            # Still run gesture detection on the raw frame
            direction = gesture.detect_gesture(frame)
            if direction is not None:
                handle_gesture(direction)

            cv2.imshow("ESP32 Tracker", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        flat_lines = [tuple(line[0]) for line in lines]

        # STEP 3 — Filter to vertical/horizontal
        horizontal, vertical = filter_lines(flat_lines, img)

        if len(horizontal) < 2 or len(vertical) < 2:
            direction = gesture.detect_gesture(img)
            if direction is not None:
                handle_gesture(direction)

            cv2.imshow("ESP32 Tracker", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # STEP 4 — Extend lines to full-image
        H, W = img.shape[:2]
        ext_h = [extend_segment(*h, W, H) for h in horizontal]
        ext_v = [extend_segment(*v, W, H) for v in vertical]

        # STEP 5 — Compute intersections
        all_points = []
        for hx1, hy1, hx2, hy2 in ext_h:
            for vx1, vy1, vx2, vy2 in ext_v:
                p = intersect(hx1, hy1, hx2, hy2, vx1, vy1, vx2, vy2)
                if p is not None:
                    all_points.append(p)

        if len(all_points) < 4:
            direction = gesture.detect_gesture(img)
            if direction is not None:
                handle_gesture(direction)

            cv2.imshow("ESP32 Tracker", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # STEP 6 — Choose TL, TR, BR, BL
        corners = extract_corners_from_points(all_points)
        if corners is None:
            direction = gesture.detect_gesture(frame)
            if direction is not None:
                handle_gesture(direction)

            cv2.imshow("ESP32 Tracker", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        TL, TR, BR, BL = corners

        # STEP 7 — Harris refinement (local)
        refined = refine_corners_harris(img, [TL, TR, BR, BL], search=4)

        # STEP 8 — Temporal smoothing
        smoothed = smoother.smooth(refined)

        # STEP 9 — Hand gesture detection (on full frame)
        direction = gesture.detect_gesture(frame)
        if direction is not None:
            handle_gesture(direction)

        # STEP 10 — Draw final 4 corners
        vis = draw_corners(img.copy(), smoothed, color=(0, 255, 0), radius=10)

        cv2.imshow("ESP32 Tracker", vis)

        # Quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
