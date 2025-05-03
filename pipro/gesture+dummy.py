import cv2
import numpy as np
from collections import deque
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Video stream
cap = cv2.VideoCapture('http://192.168.142.189:8080/?action=stream')
q
# Blue object tracking
prev_positions = deque(maxlen=10)
movement_threshold = 15

# Gesture state
tracking_enabled = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame")
        break

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)

    # Detect hands
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    num_hands = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            num_hands += 1

    # Gesture logic for controlling tracking
    if num_hands == 2:
        tracking_enabled = False
        cv2.putText(frame, "STOPPED - Two hands", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    elif num_hands == 1 and not tracking_enabled:
        tracking_enabled = True
        cv2.putText(frame, "RESUMED - One hand gesture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Tracking logic (runs only when enabled)
    if tracking_enabled:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            center_x = x + w // 2
            prev_positions.append(center_x)

            if len(prev_positions) == prev_positions.maxlen:
                movement = prev_positions[-1] - prev_positions[0]
                if abs(movement) > movement_threshold:
                    if movement > 0:
                        print("Moving right")
                    else:
                        print("Moving left")
                else:
                    print("Moving forward")
        else:
            print("No blue object detected")

        cv2.putText(frame, "TRACKING ENABLED", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

    else:
        cv2.putText(frame, "TRACKING DISABLED", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 100, 255), 2)

    cv2.imshow("Gesture Control with Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
