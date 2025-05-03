

https://github.com/user-attachments/assets/38f400ed-5705-4a98-9633-374bf222be3d

# Human-Following-Robot-
The Human Following Robot uses YOLOv8n for person detection, dynamic HSV tracking, MediaPipe for gesture control, and dual PID for motion. It maintains distance, avoids obstacles, and responds to hand gestures. A Flask web app shows live video and stats. Optimized with Kalman filter, frame skipping, and React-based UI.

# 🤖 Human Following Robot

A smart, vision-based robot that autonomously follows a specific person using real-time object detection, gesture commands, and smooth motion control. Designed with performance, adaptability, and usability in mind.

## 🔍 Features

- **Person Detection**: YOLOv8n (ultralight model) for real-time human recognition.
- **Dynamic HSV Tracking**: Adaptive color segmentation for robustness in varying lighting.
- **Pose Estimation**: Tracks orientation and movement direction.
- **Gesture Control**: MediaPipe-based hand gestures (open = follow, fist = stop).
- **Motion Control*

https://github.com/user-attachments/assets/16137667-dcc5-485f-9913-b5e6b1eb7daa

*: Dual PID controllers for distance and steering.
- **Fallback Mode**: Automatically searches for the user if lost from view.
- **Live Monitoring**: Flask-based app streams video and system stats.
- **Frontend Dashboard**:
  - Built with React + Vite + TypeScript
  - Styled using Tailwind CSS and shadcn-ui
  - Includes PID tuning and mode toggle options

## ⚙️ Tech Stack

- **Computer Vision**: YOLOv8n, OpenCV, MediaPipe
- **Control System**: PID controllers, Kalman filter (evaluated)
- **Web Interface**: Flask (backend), React + Vite (frontend)
- **Optimization**: Frame skipping, quantization (INT8), 320×240 resolution
- **Performance**: Achieves 8–12 FPS with over 95% detection accuracy

## 🧠 Concepts Used

- Object Detection
- HSV Color Segmentation
- Multithreading
- Gesture Recognition
- PID Control System
- Real-time Web Streaming
- Kalman Filtering (for smooth tracking)

## 📷 recordings of the project



## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for frontend)
- A webcam or camera module
- Raspberry Pi / Jetson Nano / PC

├── backend/ # Flask server for video streaming & PID tuning
├── pipro/ # Raspberry Pi-side code (YOLO, HSV tracking, gestures, PID)
├── smart-follow-bot/ # Main logic: tracking, filtering, control integration
├── models/ # YOLOv8n weights and config
└── README.md

### Installation

```bash
# Backend
cd backend
pip install -r requirements.txt

https://github.com/user-attachments/assets/a538ffea-ef10-46e1-ba15-22be6a873106


python app.py

# Frontend
cd frontend
npm install
npm run dev

