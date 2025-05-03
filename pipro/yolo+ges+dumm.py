import cv2
import numpy as np
from collections import deque
import mediapipe as mp
from ultralytics import YOLO  # Make sure to `pip install ultralytics`

# Load YOLOv8 model (YOLOv8n is fast, yolov8s is more accurate)
model = YOLO("yolov8n.pt")  # Make sure this file is present or download from Ultralytics

# MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Stream
cap = cv2.VideoCapture('http://192.168.142.189:8080/?action=stream')
prev_positions = deque(maxlen=10)
movement_threshold = 15
tracking_enabled = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame")
        break

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    display_frame = frame.copy()

    # === YOLOv8 Human Detection ===
    results = model(frame, verbose=False)[0]
    person_detected = False
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls == 0:  # Class 0 = person
            person_detected = True
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display_frame, "Human", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # === Hand Detection ===
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    num_hands = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            num_hands += 1

    # === Gesture-Based Command Logic ===
    if person_detected:
        if num_hands == 2:
            tracking_enabled = False
            cv2.putText(display_frame, "STOPPED - Two Hands", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print("SEND COMMAND: STOP")
        elif num_hands == 1 and not tracking_enabled:
            tracking_enabled = True
            cv2.putText(display_frame, "RESUMED - One Hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print("SEND COMMAND: RESUME")
        elif tracking_enabled:
            # You can add color tracking logic here to move forward/left/right etc.
            print("SEND COMMAND: MOVING FORWARD")
    else:
        cv2.putText(display_frame, "No human detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)

    cv2.imshow("YOLOv8 + Gesture Detection", display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
