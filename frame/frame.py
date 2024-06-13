import cv2
import time
import pika
import base64
import os

def connect_rabbitmq():
    connection_attempts = 0
    max_attempts = 5
    while connection_attempts < max_attempts:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672))
            channel = connection.channel()
            print("Connected to RabbitMQ")
            return channel, connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Waiting for RabbitMQ connection... (attempt {connection_attempts+1}/{max_attempts})")
            time.sleep(7)
            connection_attempts += 1
    raise Exception("Failed to connect to RabbitMQ")

def convert_image_to_bytes(image):
    _, img_encoded = cv2.imencode('.jpg', image)
    return img_encoded.tobytes()

def extract_frames_from_video(video_path, fps_limit=1):
    try:
        channel, connection = connect_rabbitmq()
        channel.queue_declare(queue='frame')
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
                channel.basic_publish(exchange='',
                                     routing_key='frame',
                                     body=frame_bytes)
                print(f"[x] Sent frame {frame_count}")

                
                start_time = current_time
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        connection.close()

if __name__ == "__main__":
    video_path = "udp://127.0.0.1:5000"
    extract_frames_from_video(video_path)
