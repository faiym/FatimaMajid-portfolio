from flask import Flask, render_template, Response
import cv2
import os

app = Flask(__name__)

# VIDEO FILE SETUP
PROCESSED_VIDEO_FILE = 'threat detection.mp4'

def check_video_file():
    """Check if the processed video file exists"""
    if os.path.exists(PROCESSED_VIDEO_FILE):
        print(f"✅ Found processed video: {PROCESSED_VIDEO_FILE}")
        return True
    else:
        print(f"❌ Processed video not found: {PROCESSED_VIDEO_FILE}")
        print("Available files in directory:")
        for file in os.listdir('.'):
            if file.endswith('.mp4'):
                print(f"  - {file}")
        return False

@app.route('/')
def index():
    # We'll use a simple static message since the video shows the real status
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        if check_video_file():
            cap = cv2.VideoCapture(PROCESSED_VIDEO_FILE)
            print("🎬 Streaming AI-processed video with threat detection...")
        else:
            # Fallback message
            print("⚠️  Using fallback image (video not found)")
            while True:
                # Create a simple error message image
                import numpy as np
                img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(img, "VIDEO FILE NOT FOUND", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(img, "Please check: threat detection.mp4", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                ret, buffer = cv2.imencode('.jpg', img)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                return
        
        while True:
            success, frame = cap.read()
            if not success:
                # Loop the video when it ends
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Encode the frame for web streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Control playback speed
            cv2.waitKey(30)  # Better timing control

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 Starting AegisNET-VA Server...")
    print("🌐 Open: http://localhost:5000")
    print("📹 Streaming AI-processed threat detection video")
    check_video_file()
    app.run(debug=True, port=5000)