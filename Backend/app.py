from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading
import time
import cv2
import numpy as np
import socket
import json
from ultralytics import YOLO

app = Flask(__name__)
socketio = SocketIO(app)

# Configuration
STREAM_URL = 'http://192.168.142.130:8080/?action=stream'
PI_IP = "192.168.142.130"
PI_PORT = 65432
HSV_LOWER = np.array([0, 100, 100])    # Maroon lower HSV (adjust accordingly)
HSV_UPPER = np.array([10, 255, 255])   # Maroon upper HSV

# Global states
auto_active = False
current_frame = None
frame_lock = threading.Lock()
tracking_data = {
    'fps': 0.0,
    'tracking': False,
    'warning': '',
    'action': 'stop',
    'speed': 0
}

# Initialize camera
cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 312)
cap.set(cv2.CAP_PROP_FPS, 30)

# Load YOLO model
model = YOLO("yolov8n.pt")

def send_motor_command(action, speed=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((PI_IP, PI_PORT))
            cmd = {"action": action}
            if speed is not None:
                cmd["speed"] = speed
            s.sendall((json.dumps(cmd) + '\n').encode())
            return s.recv(1024).decode() == "ACK"
    except Exception as e:
        print(f"Motor error: {e}")
        return False

def auto_tracking():
    global auto_active, current_frame, tracking_data
    
    # Tracking variables
    tracker = None
    prev_bbox = None
    frame_count = 0
    start_time = time.time()
    last_yolo = time.time()
    
    while auto_active:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue
        
        # Processing frame
        processed_frame, status = process_frame(frame, last_yolo)
        
        # Update tracking data
        with frame_lock:
            current_frame = processed_frame
            tracking_data.update(status)
            frame_count += 1
            tracking_data['fps'] = frame_count / (time.time() - start_time)
        
        # Send motor commands
        handle_movement(status)
        
        # Send updates to UI
        socketio.emit('tracking_update', tracking_data)
        
        time.sleep(0.01)
    
    send_motor_command("stop")

def process_frame(frame, last_yolo):
    global tracker, prev_bbox
    status = {'tracking': False, 'warning': '', 'action': 'stop', 'speed': 0}
    
    # YOLO detection
    bbox = None
    if time.time() - last_yolo > 0.5:
        results = model(frame, classes=[0], conf=0.3, verbose=False)
        for result in results:
            boxes = result.boxes.xywh.cpu().numpy()
            if len(boxes) > 0:
                box = boxes[0]
                x, y, w, h = map(int, [box[0]-box[2]/2, box[1]-box[3]/2, box[2], box[3]])
                bbox = (x, y, w, h)
                last_yolo = time.time()
    
    # HSV tracking
    if bbox:
        x, y, w, h = bbox
        roi = frame[y-20:y+h+20, x-20:x+w+20]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            max_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_contour) > 100:
                x, y, w, h = cv2.boundingRect(max_contour)
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, (x, y, w, h))
                prev_bbox = (x, y, w, h)
                status['tracking'] = True
    
    # Draw UI elements
    if prev_bbox:
        x, y, w, h = prev_bbox
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "TRACKING", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.putText(frame, f"FPS: {tracking_data['fps']:.1f}", (10, frame.shape[0]-10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame, status

def handle_movement(status):
    # Your movement logic here
    pass  # Add your specific movement commands

def gen_frames():
    while True:
        with frame_lock:
            if current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auto')
def auto_page():
    return render_template('auto.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('auto_control')
def handle_auto_control(command):
    global auto_active
    if command == 'start' and not auto_active:
        auto_active = True
        threading.Thread(target=auto_tracking).start()
        socketio.emit('system_status', {'status': 'running'})
    elif command == 'stop':
        auto_active = False
        socketio.emit('system_status', {'status': 'stopped'})

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    finally:
        auto_active = False
        cap.release()
        cv2.destroyAllWindows()