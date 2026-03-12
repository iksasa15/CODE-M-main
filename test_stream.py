import cv2
url = "http://192.168.8.12:81/stream"
cap = cv2.VideoCapture(url)
if cap.isOpened():
    print("Stream opened successfully!")
    ret, frame = cap.read()
    if ret:
        print("Frame captured!")
    else:
        print("Failed to capture frame.")
else:
    print("Failed to open stream.")
cap.release()
