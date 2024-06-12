import cv2
import time

def extract_frames_from_video():
    
    cap = cv2.VideoCapture("udp://127.0.0.1:5000")
    frame_count = 0
    start_time = time.time()

    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = time.time()
        if current_time - start_time >= 1:
            frame_count += 1
            file_name = f"frame_{frame_count}.jpg"
            cv2.imwrite(file_name, frame)
            start_time = current_time
    
    cap.release()

if __name__ == "__main__":
    extract_frames_from_video()
