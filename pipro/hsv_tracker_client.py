
import cv2
import numpy as np
import socket

# Pi IP and port
PI_IP = '192.168.142.189'  # Replace with your Pi's IP
PORT = 12345
sock = socket.socket()
sock.connect((PI_IP, PORT))

# HSV range for object (adjust for your color)
LOWER = np.array([30, 150, 50])   # Example: green lower HSV
UPPER = np.array([70, 255, 255])  # Example: green upper HSV

# Start webcam
cap = cv2.VideoCapture(0)

def send_command(cmd):
    print(f"[SEND] {cmd}")
    sock.send((cmd + '\n').encode())

last_command = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER, UPPER)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cx = cy = 0
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area > 500:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)

                center_x = frame.shape[1] // 2
                diff = cx - center_x

                if abs(diff) < 50:
                    command = "FORWARD"
                elif diff < -50:
                    command = "LEFT"
                else:
                    command = "RIGHT"
            else:
                command = "STOP"
        else:
            command = "STOP"
    else:
        command = "STOP"

    if command != last_command:
        send_command(command)
        last_command = command

    cv2.imshow("Tracking", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        send_command("STOP")
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
