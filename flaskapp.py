from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO

# -------------------------------
# 1️⃣ Initialize Flask and YOLO
# -------------------------------
app = Flask(__name__)

# Load your trained model
model_path = r"C:\Users\Meraki\Desktop\aegisnet_demo\hituav_drone_detector.pt"
model = YOLO(model_path)

# -------------------------------
# 2️⃣ Real-time frame generator
# -------------------------------
def generate_frames():
    camera = cv2.VideoCapture(0)  # Use webcam (0), or replace with video file path
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Run detection
        results = model(frame, conf=0.4)

        # Annotate frame
        annotated_frame = results[0].plot()

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield frame in byte format for Flask streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# -------------------------------
# 3️⃣ Flask routes
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')  # simple HTML page to display video

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def get_detections():
    # Optional: return info about model or detections
    return jsonify({
        'model': 'HIT-UAV Drone Detector',
        'accuracy': '88.9% mAP50',
        'info': 'Infrared/Thermal drone detection'
    })

# -------------------------------
# 4️⃣ Run Flask app
# -------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
