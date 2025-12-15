import cv2
import numpy as np
import os

# ESP32 stream URL
STREAM_URL = "http://192.168.4.35/high-quality-stream"

# Create auto-increment save directory
base_folder = "captured_frames"

SAVE_DIR = base_folder
count = 2

while os.path.exists(SAVE_DIR):
    SAVE_DIR = f"{base_folder}_{count}"
    count += 1

os.makedirs(SAVE_DIR)
print(f"📁 Saving images to: {SAVE_DIR}")

# Frame counter
save_count = 0

# Mouse callback: save frame when user clicks
def save_frame(event, x, y, flags, param):
    global save_count, current_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        filename = os.path.join(SAVE_DIR, f"frame_{save_count:02d}.jpg")
        cv2.imwrite(filename, current_frame)
        print(f"💾 Saved: {filename}")
        save_count += 1


# Start stream
cap = cv2.VideoCapture(STREAM_URL)
if not cap.isOpened():
    print("ESP32 Stream not working")
    exit()

cv2.namedWindow("Live Stream")
cv2.setMouseCallback("Live Stream", save_frame)

print("🎥 Live feed running — click the window to save frames, press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("No frame received.")
        continue

    current_frame = frame.copy()

    cv2.imshow("Live Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Exiting...")
cap.release()
cv2.destroyAllWindows()
