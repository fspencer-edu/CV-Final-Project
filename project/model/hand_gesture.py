import cv2
import mediapipe as mp
import numpy as np
import time

class HandGestureController:
    def __init__(self, smoothing=0.3, min_swipe=35, cooldown=0.4):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.last_pos = None
        self.smoothing = smoothing
        self.min_swipe = min_swipe
        self.last_trigger = 0
        self.cooldown = cooldown

    def detect_gesture(self, frame, box=None):
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            self.last_pos = None
            return None

        lm = result.multi_hand_landmarks[0]

        # --- index fingertip ---
        ix = int(lm.landmark[8].x * w)
        iy = int(lm.landmark[8].y * h)
        current = np.array([ix, iy], dtype=float)

        # draw fingertip
        cv2.circle(frame, (ix, iy), 10, (0, 255, 0), -1)

        # BOX CONSTRAINT
        if box is not None:
            TL, TR, BR, BL = box

            x_min = min(TL[0], BL[0])
            x_max = max(TR[0], BR[0])
            y_min = min(TL[1], TR[1])
            y_max = max(BL[1], BR[1])

            if not (x_min < ix < x_max and y_min < iy < y_max):
                # Finger is outside the box → ignore
                self.last_pos = None
                return None

        # initialize tracking
        if self.last_pos is None:
            self.last_pos = current
            return None

        # --- smoothing ---
        smoothed = (1 - self.smoothing) * self.last_pos + self.smoothing * current

        dx = smoothed[0] - self.last_pos[0]
        dy = smoothed[1] - self.last_pos[1]
        self.last_pos = smoothed

        dist = np.hypot(dx, dy)
        now = time.time()

        if dist < self.min_swipe:
            return None

        if now - self.last_trigger < self.cooldown:
            return None

        self.last_trigger = now

        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
