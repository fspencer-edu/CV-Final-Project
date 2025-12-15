import cv2
import mediapipe as mp

STREAM_URL = "http://192.168.4.35/high-quality-stream" 

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def main():

    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        raise RuntimeError("Cannot open stream")

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    # Draw landmarks on image
                    mp_draw.draw_landmarks(
                        frame, handLms, mp_hands.HAND_CONNECTIONS
                    )

                    # Show fingertip of Index Finger
                    h, w, _ = frame.shape
                    index_tip = handLms.landmark[8]
                    cx, cy = int(index_tip.x * w), int(index_tip.y * h)

                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)
                    cv2.putText(frame, f"Index: {cx},{cy}",
                                (cx+20, cy),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,0), 2)

            cv2.imshow("Hand Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
