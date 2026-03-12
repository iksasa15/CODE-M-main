import cv2
import requests
import os
import time
from config import STREAM_URL

# ======================================================================
engine = None
try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice_index = 1 if len(voices) > 1 else 0
    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty("rate", 140)
except Exception:
    pass

def AI_speak(something):
    if engine:
        try:
            engine.say(something)
            engine.runAndWait()
        except Exception:
            print(something)
    else:
        print(something)
    return something

# ======================================================================

def get_color_name(hsv_pixel):
    hue_value = hsv_pixel[0]
    saturation = hsv_pixel[1]
    value = hsv_pixel[2]

    color = "Undefined"
    if saturation < 20:
        if value > 200:
            color = "White"
        else:
            color = "Gray" if value > 50 else "Black"
    elif hue_value < 5 or hue_value > 175:
        color = "Red"
    elif hue_value < 22:
        color = "Orange"
    elif hue_value < 33:
        color = "Yellow"
    elif hue_value < 78:
        color = "Green"
    elif hue_value < 130:
        color = "Blue"
    elif hue_value < 170:
        color = "Magenta"
    else:
        color = "Purple"

    # Refine colors
    if color == "Magenta" and value > 200:
        color = "Pink"
    if color == "Red" and value < 50:
        color = "Maroon"
    if color == "Orange" and value < 100:
        color = "Brown"
        
    return color

# ======================================================================

# ======================================================================

def run_live_detection():
    # Use the snapshot URL if the stream port 81 is unstable
    # Or keep using stream if you prefer, but we'll add better handling
    stream_url = STREAM_URL
    snapshot_url = f"http://192.168.8.12/capture" 
    
    print(f"Connecting to stream: {stream_url}")
    cap = cv2.VideoCapture(stream_url)
    
    # Set a shorter timeout for OpenCV
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000000" # 5 seconds in microseconds

    last_speak_time = 0
    
    while True:
        ret, frame = cap.read()
        
        # If stream fails, try to reconnect or use snapshots
        if not ret:
            print("Stream interrupted. Falling back to snapshot mode...")
            try:
                resp = requests.get(snapshot_url, timeout=5)
                if resp.status_code == 200:
                    import numpy as np
                    nparr = np.frombuffer(resp.content, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                else:
                    time.sleep(1)
                    continue
            except Exception as e:
                print(f"Connection error: {e}")
                time.sleep(2)
                cap.open(stream_url) # Try to reopen stream
                continue

        if frame is None:
            continue

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape

        cx = int(width / 2)
        cy = int(height / 2)

        # Pick pixel value at center
        pixel_center = hsv_frame[cy, cx]
        current_color = get_color_name(pixel_center)

        # Speak the color every 3 seconds
        if time.time() - last_speak_time > 3:
            AI_speak(current_color)
            last_speak_time = time.time()

        # Draw UI
        pixel_center_bgr = frame[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])
        
        cv2.putText(frame, current_color, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (b, g, r), 3)
        cv2.circle(frame, (cx, cy), 15, (255, 255, 255), 2) 
        cv2.imshow('Live Color Detection', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_detection()
