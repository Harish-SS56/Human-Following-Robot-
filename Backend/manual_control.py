from flask import Blueprint, render_template
from flask_socketio import SocketIO
from shared_config import send_motor_command, get_camera
import threading

manual_bp = Blueprint('manual', __name__)
socketio = SocketIO()
cap = get_camera()
active_commands = set()
speed = 60

@manual_bp.route('/manual')
def manual():
    return render_template('manual.html')

@socketio.on('manual_command')
def handle_manual(data):
    global active_commands
    command = data['command']
    state = data['state']
    
    if state:
        active_commands.add(command)
    else:
        active_commands.discard(command)
    
    process_commands()

def process_commands():
    if not active_commands:
        send_motor_command("stop")
        return
    
    # Handle combination commands
    if 'forward' in active_commands:
        if 'left' in active_commands:
            send_motor_command("forward-left", speed)
        elif 'right' in active_commands:
            send_motor_command("forward-right", speed)
        else:
            send_motor_command("forward", speed)
    elif 'backward' in active_commands:
        if 'left' in active_commands:
            send_motor_command("backward-left", speed)
        elif 'right' in active_commands:
            send_motor_command("backward-right", speed)
        else:
            send_motor_command("backward", speed)
    elif 'left' in active_commands:
        send_motor_command("left", speed)
    elif 'right' in active_commands:
        send_motor_command("right", speed)

def gen_frames():
    while True:
        ret, frame = cap.read()
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')