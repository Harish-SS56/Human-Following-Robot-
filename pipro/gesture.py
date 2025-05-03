import cv2
import mediapipe as mp

# Init MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture('http://192.168.142.189:8080/?action=stream')

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame")
        break

    frame = cv2.flip(frame, 1)  # Mirror for natural interaction
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    num_hands = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            num_hands += 1

    # Gesture logic
    if num_hands == 2:
        print("STOP - Two hands detected")
    elif num_hands == 1:
        print("START/CONTINUE - One hand detected")
    else:
        print("No hands - IDLE")

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
