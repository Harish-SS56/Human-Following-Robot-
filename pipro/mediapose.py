import cv2
import numpy as np
import mediapipe as mp
import time
from collections import deque
import pyttsx3  # Optional: PC speaker

# Init PC speaker (comment out if not needed)
engine = pyttsx3.init()
engine.setProperty('rate', 150)
def speak(text):
    engine.say(text)
    engine.runAndWait()

# MediaPipe Setup
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
pose = mp_pose.Pose(min_detection_confidence=0.5)

# Video stream
cap = cv2.VideoCapture('http://192.168.142.189:8080/?action=stream')

prev_positions = deque(maxlen=10)
gesture_mode = False
last_seen = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    hand_result = hands.process(rgb)
    pose_result = pose.process(rgb)

    num_hands = 0
    if hand_result.multi_hand_landmarks:
        for lm in hand_result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            num_hands += 1

    # Gesture control
    if num_hands == 2:
        gesture_mode = False
        cv2.putText(frame, "STOP", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    elif num_hands == 1:
        if not gesture_mode:
            speak("Started following")
        gesture_mode = True
        cv2.putText(frame, "START", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # If allowed to follow
    if gesture_mode:
        if pose_result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            nose = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            h, w, _ = frame.shape
            cx, cy = int(nose.x * w), int(nose.y * h)
            prev_positions.append(cx)

            if len(prev_positions) == 10:
                delta = prev_positions[-1] - prev_positions[0]
                if abs(delta) < 10:
                    movement = "FORWARD"
                elif delta > 10:
                    movement = "RIGHT"
                else:
                    movement = "LEFT"
                cv2.putText(frame, movement, (cx, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                print(movement)

            last_seen = time.time()
        else:
            # HSV fallback
            lower_blue = np.array([100, 150, 50])
            upper_blue = np.array([140, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                center_x = x + w // 2
                prev_positions.append(center_x)

                if len(prev_positions) == 10:
                    delta = prev_positions[-1] - prev_positions[0]
                    if abs(delta) < 10:
                        movement = "FORWARD"
                    elif delta > 10:
                        movement = "RIGHT"
                    else:
                        movement = "LEFT"
                    print(movement)
                last_seen = time.time()
            else:
                # No person detected
                if time.time() - last_seen > 3:
                    print("No person found. Searching...")
                    speak("Searching for person")
                    last_seen = time.time()  # Avoid spamming

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
