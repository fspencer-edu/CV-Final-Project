# CV-Final-Project

- Attached:
    - ESP32 Camera module stream (arduino code)
    - Program source code
    - Demo
    - Final paper


# Computer Vision Project: Real-Time 3D Tracking & Gesture Navigation

Fiona Spencer
501116950
Group#: 22
Dec 15, 2025

## Project Structure

```c
├── README.md
├── analysis
│   ├── SIFT2.ipynb
│   ├── bundle.ipynb
│   ├── calibration.ipynb
│   ├── capture.py
│   ├── captured_frames
│   ├── corner.ipynb
│   ├── filter.ipynb
│   ├── hough.ipynb
│   └── stereo
├── app
│   ├── hand_det.py
│   ├── run.py
│   └─ stream_corners.py
├── assets
│   └── checkerboard.png
├── cv_env.yml
├── data
│   └── CALI
├── model
│   ├── __pycache__
│   ├── bundle.py
│   ├── calibration_data.py
│   ├── checkerboard.py
│   ├── corners.py
│   └── hand_gesture.py
├── setup
│   ├── cali_cam.py
│   ├── cali_pipeline.py
│   ├── clean.py
│   ├── gen_cali.py
│   └── preprocess.py
└── utils
    ├── __pycache__
    ├── filters.py
    ├── find_blur.py
    └── find_noise.py
```

## Setup

- To initialize the system, install requirements, then begin by running the calibration pipeline from the project root: `python setup/cali_pipeline.py`

    - This script captures 50 calibration images of a checkerboard pattern when detected by the camera. The captured images are automatically cleaned using blur and noise detection, then preprocessed to enhance image quality. Using the processed images, the pipeline performs camera calibration and computes the intrinsic parameters (focal length, principal point, and lens distortion) as well as extrinsic parameters (rotation and translation vectors). The resulting calibration data are saved for use by the application.

- Once calibration is complete, launch the main application: `python app/stream_corners.py`

    - This starts the real-time system, which detects the calibrated corner geometry, establishes the region of interest, and performs egocentric hand-gesture tracking within the bounded area. Detected corners and hand landmarks are visualized live from the camera stream.

## Introduction
This project develops a real-time system for screen boundary detection and gesture-based interaction using an ESP32 camera module. Screen corners are localized through a geometric pipeline combining Canny edge detection, Hough line extraction, segment intersection, and Harris corner refinement, providing stable tracking even under motion and partial occlusion.

Hand gestures are recognized using MediaPipe, enabling swipe and pinch actions to trigger operating-system controls. A checkerboard-based calibration stage supplies the intrinsic and extrinsic camera parameters required for geometric consistency, pose estimation, and accurate spatial interpretation. Together, these components form an efficient computer-vision framework for non-contact interaction with digital displays.

## Objective
The project aims to develop a vision-based interaction system that makes a standard display behave as a touch-responsive surface using only a monocular camera. Inspired by AR and VR interfaces that rely on gesture-driven control, the system combines real-time screen boundary detection, Harris-refined corner tracking, and camera calibration using checkerboard-derived intrinsic and extrinsic parameters to maintain spatial consistency. Hand-gesture recognition enables directional control and pinch-based actions, creating a lightweight framework where users can manipulate on-screen content through mid-air gestures without specialized hardware.


## Methods
The experimental methodology integrates multiple computer-vision pipelines to detect, calibrate, and track a display surface for gesture-based interaction. Screen boundaries are estimated using Canny edge extraction followed by Hough line detection to isolate dominant vertical and horizontal lines whose intersections provide coarse corner locations. These corners are then refined locally using Harris corner response to increase positional precision. Camera calibration is performed using a checkerboard dataset, where intrinsic and extrinsic parameters are estimated via solvePnP and subsequently improved through bundle adjustment to minimize reprojection error across all calibration frames. The calibrated parameters enable stable projection and spatial consistency throughout tracking. Real-time operation uses continuous frame processing, temporal smoothing of corner estimates, and pose recovery via PnP when required. Hand-gesture recognition is implemented using MediaPipe to detect fingertip and palm trajectories, with directional gestures mapped to on-screen navigation commands.

## Status
The project is nearly complete, with the main screen-tracking pipeline, camera calibration system, and hand-gesture detection all functioning; the remaining tasks include finalizing the unified GUI application, improving gesture-control responsiveness, adding a 3D visualization of the camera’s position in world coordinates, and performing integration testing across different screen types to ensure consistent, reliable performance.


## Timeline
The project timeline shows steady and structured development from early November through late December, beginning with foundational analysis, ESP32 streaming tests, and early corner-detection experiments. Core components—Canny and Hough processing, Harris refinement, calibration capture, and gesture-to-OS interaction—were progressively completed throughout the month, forming a stable tracking pipeline. The remaining work focuses on integrating all modules into a unified Tkinter GUI, adding a real-time 3D Plotly visualization of the camera’s world-coordinate pose, optimizing performance on the ESP32 stream, and running full integration tests across different screen types. These upcoming tasks will complete the system and prepare it for final documentation and delivery.



| **Date**        | **Objective**                                    | **Status**   |
| --------------- | ------------------------------------------------ | ------------ |
| **Nov 1, 2025** | Initial project analysis + requirement gathering | 🟢 Completed |
| **Nov 2, 2025** | Test ESP32 stream, connectivity                  | 🟢 Completed |
| **Nov 2, 2025** | Evaluate corner detection methods                | 🟢 Completed |
| **Nov 4, 2025** | Add blur/noise filtering utilities               | 🟢 Completed |
| **Nov 4, 2025** | Screen boundary extraction (filters)             | 🟢 Completed |
| **Nov 9, 2025** | Implement Canny + Hough detection                | 🟢 Completed |
| **Nov 9, 2025** | Implement Harris corner refinement               | 🟢 Completed |
| **Nov 9, 2025** | Modularize project into model                    | 🟢 Completed |
| **Nov 12, 2025** | Test calibration pipeline + capture             | 🟢 Completed |
| **Nov 10, 2025** | Screen corner extraction pipeline               | 🟢 Completed |
| **Nov 22, 2025** | Harris refinement + temporal smoothing          | 🟢 Completed |
| **Nov 22, 2025** | Integrate MediaPipe hand detection              | 🟢 Completed |
| **Nov 23, 2025** | Build gesture → OS control layer                | 🟢 Completed |
| **Nov 30, 2025** | 3D plotly visualization of camera & screen      | 🟢 Completed |
| **Nov 30, 2025** | Tkinter GUI: calibration workflow               | 🟢 Completed |
| **Dec 4, 2025**  | Full integration test                           | 🟢 Completed |
| **Dec 4, 2025**  | Performance tuning for ESP32 stream             | 🟢 Completed |
| **Dec 10, 2025** | Finizalize Paper + README                       | 🟢 Completed |
| **Dec 15, 2025** | SUBMIT                                          | 🟢 Completed |