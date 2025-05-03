import cv2
import numpy as np
import mediapipe as mp
import time
from collections import deque
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Slower speech rate for clarity

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Configure models
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    model_complexity=1
)

pose = mp_pose.Pose(
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
    model_complexity=1,
    enable_segmentation=False
)

# Connect to Raspberry Pi camera stream
PI_CAM_URL = 'http://192.168.142.189:8080/?action=stream'
cap = cv2.VideoCapture(PI_CAM_URL)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Tracking variables
prev_positions = deque(maxlen=8)
gesture_mode = False
tracking_mode = "None"
fps_history = deque(maxlen=30)
last_gesture_time = time.time()
last_voice_time = time.time()  # To prevent voice spamming

# Performance metrics
processing_times = deque(maxlen=30)
network_latencies = deque(maxlen=30)

# Speed classification
SPEED_THRESHOLDS = {
    'fast': (0, 0.12),
    'medium': (0.12, 0.25),
    'slow': (0.25, 1.0)
}

def get_speed_category(bbox_area, frame_area):
    ratio = bbox_area / frame_area
    for speed, (min_th, max_th) in SPEED_THRESHOLDS.items():
        if min_th <= ratio < max_th:
            return speed
    return 'unknown'

def draw_metrics(frame, fps, mode, speed, proc_time, net_lat):
    y_start = 20
    line_height = 25
    colors = {
        'fast': (0, 0, 255),    # Red
        'medium': (0, 165, 255), # Orange
        'slow': (0, 255, 0)     # Green
    }
    
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, y_start), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    cv2.putText(frame, f"Mode: {mode}", (10, y_start + line_height), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    cv2.putText(frame, f"Speed: {speed}", (10, y_start + 2*line_height), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors.get(speed, (255, 255, 255)), 1)
    cv2.putText(frame, f"Proc: {proc_time:.1f}ms", (10, y_start + 3*line_height), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
    cv2.putText(frame, f"Net: {net_lat:.1f}ms", (10, y_start + 4*line_height), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 255), 1)

# Main loop
prev_frame_time = time.time()
person_detected = False
while True:
    # Network latency measurement
    net_start = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Connection lost - retrying...")
        cap.release()
        cap = cv2.VideoCapture(PI_CAM_URL)
        time.sleep(1)
        continue
    
    network_latencies.append((time.time() - net_start) * 1000)
    
    # Processing start time
    proc_start = time.time()
    
    frame = cv2.flip(frame, 1)
    frame_area = frame.shape[0] * frame.shape[1]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Gesture control (hand detection)
    hand_result = hands.process(rgb)
    num_hands = len(hand_result.multi_hand_landmarks) if hand_result.multi_hand_landmarks else 0
    
    # Improved gesture control logic
    if num_hands == 2:
        # Two hands detected - stop tracking
        gesture_mode = False
        tracking_mode = "None"
        cv2.putText(frame, "STOP (Two hands)", (frame.shape[1]//2 - 100, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    elif num_hands == 1 and not gesture_mode:
        # One hand detected and not currently tracking - start tracking
        gesture_mode = True
        tracking_mode = "MediaPipe"
        cv2.putText(frame, "START (One hand)", (frame.shape[1]//2 - 100, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        last_gesture_time = time.time()
    
    bbox = None
    speed_category = "none"
    bbox_area_ratio = 0
    current_person_detected = False
    
    if gesture_mode:
        # Try MediaPipe pose detection first
        pose_result = pose.process(rgb)
        
        if pose_result.pose_landmarks:
            current_person_detected = True
            tracking_mode = "MediaPipe"
            landmarks = pose_result.pose_landmarks.landmark
            
            # Get bounding box from key points
            key_points = [
                mp_pose.PoseLandmark.LEFT_SHOULDER,
                mp_pose.PoseLandmark.RIGHT_SHOULDER,
                mp_pose.PoseLandmark.LEFT_HIP,
                mp_pose.PoseLandmark.RIGHT_HIP,
                mp_pose.PoseLandmark.NOSE
            ]
            
            xs = []
            ys = []
            for point in key_points:
                lm = landmarks[point]
                if lm.visibility > 0.3:
                    xs.append(lm.x)
                    ys.append(lm.y)
            
            if xs and ys:
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                # Convert to pixel coordinates
                h, w = frame.shape[:2]
                x1, y1 = int(min_x * w), int(min_y * h)
                x2, y2 = int(max_x * w), int(max_y * h)
                
                bbox = (x1, y1, x2, y2)
                bbox_area = (x2 - x1) * (y2 - y1)
                bbox_area_ratio = bbox_area / frame_area
                speed_category = get_speed_category(bbox_area, frame_area)
                
                # Draw pose and bbox
                mp_drawing.draw_landmarks(frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{speed_category} (MP)", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Fallback to HSV tracking if no pose detected
        elif time.time() - last_gesture_time > 2:
            tracking_mode = "HSV"
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([140, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Morphological operations
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 300:
                    current_person_detected = True
                    x, y, w, h = cv2.boundingRect(largest)
                    bbox = (x, y, x+w, y+h)
                    bbox_area = w * h
                    bbox_area_ratio = bbox_area / frame_area
                    speed_category = get_speed_category(bbox_area, frame_area)
                    
                    # Draw HSV bbox
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, f"{speed_category} (HSV)", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
    
    # Voice feedback for person detection
    if gesture_mode and not current_person_detected:
        if time.time() - last_voice_time > 5:  # Only speak every 5 seconds
            speak("Searching for person")
            last_voice_time = time.time()
        cv2.putText(frame, "SEARCHING FOR PERSON", (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    person_detected = current_person_detected
    
    # Calculate processing time
    proc_time = (time.time() - proc_start) * 1000
    processing_times.append(proc_time)
    
    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_frame_time)
    prev_frame_time = current_time
    fps_history.append(fps)
    
    # Display mode status
    mode_status = f"{'ACTIVE' if gesture_mode else 'INACTIVE'} ({tracking_mode})"
    cv2.putText(frame, mode_status, (frame.shape[1] - 200, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255) if not gesture_mode else (0, 255, 0), 2)
    
    # Display metrics
    avg_proc_time = sum(processing_times)/len(processing_times) if processing_times else 0
    avg_net_latency = sum(network_latencies)/len(network_latencies) if network_latencies else 0
    avg_fps = sum(fps_history)/len(fps_history) if fps_history else 0
    draw_metrics(frame, avg_fps, tracking_mode, speed_category, avg_proc_time, avg_net_latency)
    
    cv2.imshow("Pi Camera Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()