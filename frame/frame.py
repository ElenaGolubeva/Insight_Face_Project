import cv2
import time
from broker.rabbitmq_class import RabbitMQBroker
from broker.kafka_class import KafkaBroker

def convert_image_to_bytes(image):
    _, img_encoded = cv2.imencode('.jpg', image)
    return img_encoded.tobytes()

def extract_frames_from_video(video_path, fps_limit=1):
    try:
        mess_broker = KafkaBroker()
        mess_broker.connect()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Failed to open video: {video_path}")

        frame_count = 0
        start_time = time.time()
        

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()
            if current_time - start_time >= 1.0 / fps_limit:
                frame_count += 1
                frame_bytes = convert_image_to_bytes(frame)
                mess_broker.publish('frame', frame_bytes)
                print(f"[x] Sent frame {frame_count}")

                
                start_time = current_time
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        mess_broker.disconnect()

if __name__ == "__main__":
    video_path = "udp://127.0.0.1:5000"
    extract_frames_from_video(video_path)