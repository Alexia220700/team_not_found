import sys
import os

# Force Python to use the correct paths
print("🔍 Debug: Checking OpenCV installation...")

try:
    # Try headless import first
    import cv2
    print(f"✅ OpenCV loaded successfully")
    print(f"   Version: {cv2.__version__}")
    print(f"   Path: {cv2.__file__}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure opencv-python-headless is installed")
    sys.exit(1)

# Continue with rest of imports
import numpy as np
from flask import Flask, Response, render_template_string

import cv2
import os
import time
from datetime import datetime
import threading
import subprocess
import socket
import webbrowser
import signal
import sys

# ============================================
# CONFIGURATION
# ============================================
iphone_ip = "your_ip_here"
port = your_port_here
username = "camera_credential"
password = "camera_credential"
stream_path = "/video"
stream_url = f"http://{username}:{password}@{iphone_ip}:{port}{stream_path}"
save_dir = "/home/arduino/iphone_captures"
os.makedirs(save_dir, exist_ok=True)

# UNO Q IP for web server
uno_q_ip = "your_arduino_ip"  # Your UNO Q's IP
web_port = your_web_port

# ============================================
# GLOBAL VARIABLES
# ============================================
latest_frame = None
frame_lock = threading.Lock()
capture_running = True
frame_count = 0
flask_thread = None
cap = None

# ============================================
# FLASK WEB SERVER SETUP
# ============================================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>📱 iPhone → UNO Q Live Stream</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial; text-align: center; background: #1a1a1a; color: white; }
        img { max-width: 90%; border: 3px solid #4CAF50; border-radius: 10px; }
        .stats { background: #333; padding: 10px; border-radius: 5px; margin: 10px; }
        .status { color: #4CAF50; font-weight: bold; }
        button { padding: 10px 20px; background: #4CAF50; color: white; border: none; 
                border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>📱 iPhone Camera → Arduino UNO Q</h1>
    <div class="stats">
        <p class="status">✅ LIVE STREAMING</p>
        <p>Frames captured: <span id="frameCount">{{ frame_count }}</span></p>
        <p>Stream URL: <code>http://{{ uno_q_ip }}:{{ web_port }}</code></p>
    </div>
    <img src="{{ url_for('video_feed') }}" width="80%">
    <p>⏱️ Auto-refreshes every 30 seconds</p>
    <p><small>Press Ctrl+C in terminal to stop everything</small></p>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main HTML page"""
    global frame_count
    return render_template_string(HTML_TEMPLATE, 
                                 frame_count=frame_count,
                                 uno_q_ip=uno_q_ip,
                                 web_port=web_port)

def generate_frames():
    """Generator function for streaming video"""
    global latest_frame
    while capture_running:
        with frame_lock:
            if latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    """Run Flask server"""
    try:
        app.run(host='Your_host', port=web_port, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"\n⚠️ Flask server note: {e}")

# ============================================
# AUTO-OPEN BROWSER FUNCTION
# ============================================
def open_browser_automatically():
    """Automatically open browser on laptop"""
    time.sleep(3)  # Wait for Flask to start
    url = f"http://{uno_q_ip}:{web_port}"
    
    print(f"\n🌐 Automatically opening browser to: {url}")
    
    try:
        # Uses webbrowser module (works on most systems)
        webbrowser.open(url)
    except:
        try:
            # Uses subprocess for more control
            if sys.platform == 'win32':
                os.startfile(url)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', url])
            else:  # Linux
                subprocess.run(['xdg-open', url])
        except:
            print(f"   Please open manually: {url}")

# ============================================
# CLEAN SHUTDOWN HANDLER
# ============================================
def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global capture_running
    print("\n\n🛑 Stopping everything...")
    capture_running = False
    
    print("   ⏳ Waiting for threads to finish...")
    time.sleep(2)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 60)
    print("✅ Clean shutdown complete!")
    print(f"📊 Final frames captured: {frame_count}")
    print("=" * 60)
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

# ============================================
# MAIN CAPTURE LOOP
# ============================================
print("=" * 70)
print("🚀 iPhone → UNO Q Live Stream with Auto-Browser")
print("=" * 70)
print(f"📱 iPhone IP: {iphone_ip}")
print(f"🧠 UNO Q IP: {uno_q_ip}")
print(f"📡 Stream URL: {stream_url}")
print(f"💾 Saving frames to: {save_dir}")
print("=" * 70)

# Start Flask server
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
print("\n🌐 Web server starting...")

# Auto-open browser
browser_thread = threading.Thread(target=open_browser_automatically, daemon=True)
browser_thread.start()

print("📸 Starting video capture...")
print("✅ Stream will auto-open in your browser")
print("⏱️  Letting Flask initialize...")
time.sleep(2)

frame_count = 0
success_count = 0
start_time = time.time()

try:
    # Open video capture
    cap = cv2.VideoCapture(stream_url)
    
    if not cap.isOpened():
        print("\n❌ Failed to open stream. Troubleshooting:")
        print("   1. Is IP Camera Lite running on iPhone?")
        print("   2. Check iPhone IP: ssh to UNO Q and run: ping your_ip")
        print("   3. Verify credentials: your_credentials")
        capture_running = False
        sys.exit(1)
    
    print("✅ Connected to iPhone camera!")
    
    while capture_running:
        ret, frame = cap.read()
        
        if ret and frame is not None:
            # Update global frame for web stream
            with frame_lock:
                latest_frame = frame.copy()
            
            success_count += 1
            frame_count += 1
            
            # Save every 10th frame
            if frame_count % 10 == 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{save_dir}/frame_{timestamp}_{frame_count:06d}.jpg"
                cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                
                elapsed = time.time() - start_time
                fps = success_count / elapsed if elapsed > 0 else 0
                print(f"✅ Saved: {filename}")
                print(f"   Frames: {success_count}, FPS: {fps:.1f}")
            
            time.sleep(0.05)
            
        else:
            print("⚠️ Failed to grab frame, reconnecting...")
            time.sleep(2)
            cap.release()
            cap = cv2.VideoCapture(stream_url)
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    
finally:
    capture_running = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Program ended")
