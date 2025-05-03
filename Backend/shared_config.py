import cv2
import numpy as np
import socket
import json
import time
import pyttsx3
from ultralytics import YOLO

# HSV for green/maroon
HSV_LOWER = np.array([40, 80, 80])
HSV_UPPER = np.array([80, 255, 255])

# Socket setup
PI_IP = "192.168.58.189"
PI_PORT = 65432

# Camera setup (HTTP stream)
STREAM_URL = 'http://192.168.58.189:8080/?action=stream'
cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()

# Optimize for low latency
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 312)
cap.set(cv2.CAP_PROP_FPS, 30)

# Initialize YOLOv8 (CPU)
model = YOLO("yolov8n.pt")

# Initialize KCF tracker
tracker = None
tracker_active = False

# Initialize pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Socket client
def send_motor_command(action, speed=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((PI_IP, PI_PORT))
            cmd = {"action": action}
            if speed is not None:
                cmd["speed"] = speed
            s.sendall((json.dumps(cmd) + '\n').encode())
            response = s.recv(1024).decode()
            return response == "ACK"
    except Exception as e:
        print(f"Socket error: {e}")
        return False

# Speak text with cooldown
last_speak_time = 0
speak_cooldown = 5
def speak(text):
    global last_speak_time
    current_time = time.time()
    if current_time - last_speak_time >= speak_cooldown:
        try:
            engine.say(text)
            engine.runAndWait()
            last_speak_time = current_time
        except Exception as e:
            print(f"Audio error: {e}")

# Smooth bbox
def smooth_bbox(new_bbox, prev_bbox, alpha=0.3):
    if not new_bbox:
        return prev_bbox
    if not prev_bbox:
        return new_bbox
    x1, y1, w1, h1 = new_bbox
    x2, y2, w2, h2 = prev_bbox
    x = int(alpha * x1 + (1 - alpha) * x2)
    y = int(alpha * y1 + (1 - alpha) * y2)
    w = int(alpha * w1 + (1 - alpha) * w2)
    h = int(alpha * h1 + (1 - alpha) * h2)
    return (x, y, w, h)

# Get latest frame
def get_latest_frame(cap, max_attempts=5):
    latest_frame = None
    for _ in range(max_attempts):
        ret, frame = cap.read()
        if ret:
            latest_frame = frame
        else:
            break
    return ret, latest_frame

# Main loop
try:
    last_time = time.time()
    frame_count = 0
    fps = 0
    no_person_time = None
    last_bbox_area = None
    rotating = False
    rotation_start = None
    last_yolo_time = 0
    yolo_interval = 0.5  # Reduced CPU load
    skip_counter = 0
    fps_threshold = 10
    tracking_state = False
    prev_bbox = None
    miss_count = 0
    miss_threshold = 30  # More robust
    last_command = None

    while True:
        # Get latest frame
        ret, frame = get_latest_frame(cap)
        if not ret:
            print("Failed to grab frame")
            time.sleep(0.01)
            continue

        # Calculate FPS
        frame_count += 1
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            frame_count = 0
            last_time = current_time

        # Skip frames if FPS is low
        skip_counter += 1
        if fps < fps_threshold and skip_counter % 2 != 0:
            continue

        # Initialize bbox
        bbox = None
        hsv_tracked = False

        # Try KCF tracker if active
        if tracker_active:
            success, kcf_bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in kcf_bbox]
                if x >= 0 and y >= 0 and x + w <= frame.shape[1] and y + h <= frame.shape[0]:
                    bbox = (x, y, w, h)
                    hsv_tracked = True

        # Run YOLO periodically
        yolo_bbox = None
        max_area = 0
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        if current_time - last_yolo_time >= yolo_interval:
            results = model(frame, classes=[0], conf=0.3, verbose=False, imgsz=416)
            for result in results:
                boxes = result.boxes.xywh.cpu().numpy()
                for box in boxes:
                    x_center, y_center, w, h = box
                    area = w * h
                    if area > max_area:
                        max_area = area
                        x = int(x_center - w / 2)
                        y = int(y_center - h / 2)
                        w, h = int(w), int(h)
                        yolo_bbox = (x, y, w, h)
            last_yolo_time = current_time

        # HSV tracking if YOLO detects person
        if yolo_bbox and not bbox:
            x, y, w, h = yolo_bbox
            roi_x = max(0, x - 20)
            roi_y = max(0, y - 20)
            roi_w = min(frame_width - roi_x, w + 40)
            roi_h = min(frame_height - roi_y, h + 40)
            roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

            # HSV processing
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            hsv_bbox = None
            hsv_max_area = 0

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > hsv_max_area and area > 20:
                    hsv_max_area = area
                    hsv_bbox = cv2.boundingRect(contour)

            if hsv_bbox:
                hx, hy, hw, hh = hsv_bbox
                hx += roi_x
                hy += roi_y
                bbox = (hx, hy, hw, hh)
                hsv_tracked = True
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, (hx, hy, hw, hh))
                tracker_active = True
            else:
                bbox = yolo_bbox
                tracker_active = False

        # Smooth bbox
        if bbox:
            bbox = smooth_bbox(bbox, prev_bbox, alpha=0.3)
            prev_bbox = bbox
            miss_count = 0
        else:
            miss_count += 1
            if miss_count <= miss_threshold and prev_bbox:
                bbox = prev_bbox
                tracker_active = False
            else:
                prev_bbox = None
                tracker_active = False

        # Process bbox
        if bbox:
            x, y, w, h = bbox
            center_x = x + w // 2
            center_y = y + h // 2
            bbox_area = w * h

            # Draw bbox
            color = (0, 255, 0) if hsv_tracked or tracker_active else (255, 0, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)

            # Display
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Voice prompt
            if not tracking_state:
                speak("Following person in maroon")
                tracking_state = True

            # Reset timers
            no_person_time = None
            rotating = False
            rotation_start = None

            # Movement logic
            max_area = frame_width * frame_height
            area_ratio = bbox_area / max_area

            # Backward if too close
            if area_ratio > 0.5:
                print("Too close, moving backward")
                send_motor_command("backward", 50)
                last_command = ("backward", 50)
                last_bbox_area = bbox_area
                continue

            # Speed based on distance
            if area_ratio < 0.1:  # Far
                speed = 80
            elif area_ratio < 0.3:  # Medium
                speed = 60
            else:  # Close
                speed = 40

            # Direction based on position
            if center_x > frame_width * 0.6:  # Person is right
                print(f"Turning right at {speed}")
                send_motor_command("right", 50)
                last_command = ("right", 50)
            elif center_x < frame_width * 0.4:  # Person is left
                print(f"Turning left at {speed}")
                send_motor_command("left", 50)
                last_command = ("left", 50)
            else:  # Person is centered
                print(f"Moving forward at {speed}")
                send_motor_command("forward", speed)
                last_command = ("forward", speed)

            last_bbox_area = bbox_area
        else:
            if no_person_time is None and miss_count > miss_threshold:
                no_person_time = current_time
                rotation_start = current_time
                if tracking_state:
                    speak("Searching for person in maroon")
                    tracking_state = False
                print("No person in maroon, starting rotation")
                rotating = True
                send_motor_command("right", 30)
                last_command = ("right", 30)
            elif rotating and current_time - rotation_start >= 10:
                print("Finished rotation, stopping")
                send_motor_command("stop")
                last_command = ("stop", None)
                no_person_time = None
                rotating = False
                rotation_start = None
                if not tracking_state:
                    speak("Searching for person in maroon")
            else:
                if not rotating and miss_count > miss_threshold:
                    print("No person in maroon, stopping")
                    send_motor_command("stop")
                    last_command = ("stop", None)
                elif last_command:
                    action, speed = last_command
                    send_motor_command(action, speed)
            last_bbox_area = None
            tracking_state = False

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    send_motor_command("stop")
    cap.release()
    cv2.destroyAllWindows()
    engine.stop()