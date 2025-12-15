"""
corners.py

Reusable definitions for:
    - Canny edge detection
    - Hough line detection
    - Line filtering (orientation + length)
    - Extending lines to image borders
    - Computing intersections between lines
    - Extracting 4 geometric corners (TL, TR, BR, BL)
"""

import cv2
import numpy as np
import math


# ============================================================
# 1. Canny detector
# ============================================================
def detect_edges(img, blur=5, low=50, high=150):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if blur > 0:
        gray = cv2.GaussianBlur(gray, (blur, blur), 0)
    edges = cv2.Canny(gray, low, high)
    return edges


# ============================================================
# 2. Detect Hough lines
# ============================================================
def detect_hough_lines(edges, img_shape,
                       threshold=80,
                       min_frac=0.15,
                       max_gap=25):

    H, W = img_shape[:2]

    min_len = min_frac * W

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=threshold,
        minLineLength=min_len,
        maxLineGap=max_gap
    )

    if lines is None:
        return []

    return [tuple(line[0]) for line in lines]


# ============================================================
# 3. Filter lines by orientation
# ============================================================
def filter_lines(lines, img, vertical_thresh=10, horizontal_thresh=10):
    H, W = img.shape[:2]

    horizontal = []
    vertical = []

    for line in lines:

        x1, y1, x2, y2 = map(float, line)

        dx = x2 - x1
        dy = y2 - y1

        angle = math.degrees(math.atan2(dy, dx))
        length = math.hypot(dx, dy)

        # ---------- vertical ----------
        if abs(abs(angle) - 90) < vertical_thresh and length > H * 0.1:
            vertical.append((x1, y1, x2, y2))

        # ---------- horizontal ----------
        elif abs(angle) < horizontal_thresh and length > W * 0.1:
            horizontal.append((x1, y1, x2, y2))

    return horizontal, vertical


# ============================================================
# 4. Extend a segment to image borders
# ============================================================
def extend_segment(x1, y1, x2, y2, W, H):
    x1, y1, x2, y2 = map(float, (x1, y1, x2, y2))

    if abs(x2 - x1) < 1e-6:
        return int(x1), 0, int(x1), H

    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    y0 = b
    yW = m * W + b

    return int(0), int(y0), int(W), int(yW)


# ============================================================
# 5. Intersection of two lines
# ============================================================
def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    A = np.array([
        [x2 - x1, x3 - x4],
        [y2 - y1, y3 - y4]
    ], dtype=float)

    B = np.array([x3 - x1, y3 - y1], dtype=float)

    det = np.linalg.det(A)
    if abs(det) < 1e-9:
        return None

    t, u = np.linalg.solve(A, B)
    px = x1 + t * (x2 - x1)
    py = y1 + t * (y2 - y1)

    return (int(px), int(py))


# ============================================================
# 6. Compute all intersections between vertical/horizontal lines
# ============================================================
def compute_intersections(vertical, horizontal):
    pts = []

    for (vx1, vy1, vx2, vy2) in vertical:
        for (hx1, hy1, hx2, hy2) in horizontal:
            p = intersect(hx1, hy1, hx2, hy2, vx1, vy1, vx2, vy2)
            if p is not None:
                pts.append(p)

    return pts


# ============================================================
# 7. Extract 4 outermost corners (TL, TR, BR, BL)
# ============================================================
def extract_corners_from_points(pts):
    if len(pts) == 0:
        return None

    pts = np.array(pts, float)
    xs, ys = pts[:, 0], pts[:, 1]

    idx_TL = np.argmin(xs + ys)
    idx_TR = np.argmin(-xs + ys)
    idx_BL = np.argmin(xs - ys)
    idx_BR = np.argmin(-xs - ys)

    TL = tuple(pts[idx_TL])
    TR = tuple(pts[idx_TR])
    BR = tuple(pts[idx_BR])
    BL = tuple(pts[idx_BL])

    return [TL, TR, BR, BL]


# ============================================================
# 8. Full pipeline: get 4 corner points from an image
# ============================================================
def detect_4_corners(img):
    H, W = img.shape[:2]

    # 1. Canny
    edges = detect_edges(img)

    # 2. Hough lines
    lines = detect_hough_lines(edges, img.shape)

    if not lines:
        return None, edges, [], [], [], []

    # 3. Orientation filter
    vertical, horizontal = filter_lines(lines)

    # 4. Extend lines to full image borders
    v_ext = [extend_segment(*v, W, H) for v in vertical]
    h_ext = [extend_segment(*h, W, H) for h in horizontal]

    # 5. Intersections
    pts = compute_intersections(v_ext, h_ext)

    # 6. Extract corners
    corners = extract_corners_from_points(pts)

    return corners, edges, lines, v_ext, h_ext, pts


# Harris Refinement (local, edge-constrained)
def refine_corners_harris(image, corners, search=4):
    """
    Refines pre-estimated corner locations using Harris within a very small ROI.
    This prevents drift into screen interior or UI elements.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    refined = []

    for (cx, cy) in corners:
        cx = int(cx)
        cy = int(cy)

        # Local search window
        x1 = max(cx - search, 0)
        y1 = max(cy - search, 0)
        x2 = min(cx + search, gray.shape[1] - 1)
        y2 = min(cy + search, gray.shape[0] - 1)

        roi = gray[y1:y2, x1:x2].astype(np.float32)

        if roi.size == 0:
            refined.append((cx, cy))
            continue

        H = cv2.cornerHarris(roi, 2, 3, 0.04)
        H = cv2.dilate(H, None)

        y_local, x_local = np.unravel_index(np.argmax(H), H.shape)

        refined.append((x1 + x_local, y1 + y_local))

    return refined


def draw_corners(image, corners, color=(0, 0, 255), radius=8, thickness=-1):
    img = image.copy()

    for (x, y) in corners:
        cv2.circle(img, (int(x), int(y)), radius, color, thickness)

    return img
