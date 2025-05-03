import cv2
import numpy as np
from collections import deque

cap = cv2.VideoCapture('http://192.168.142.189:8080/?action=stream')

prev_positions = deque(maxlen=10)
movement_threshold = 15

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame")
        break

    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Blue color range
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

    # cv2.imshow("Blue Mask", mask)
    # if cv2.waitKey(1) == ord('q'):
    #     break

cap.release()
cv2.destroyAllWindows()
