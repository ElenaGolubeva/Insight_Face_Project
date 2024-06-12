import cv2
import time
import pika
import base64

def connect_rabbitmq():
    connection_attempts = 0
    max_attempts = 5
    while connection_attempts < max_attempts:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672))
            channel = connection.channel()
            print("Connected to RabbitMQ")
            return channel
        except pika.exceptions.AMQPConnectionError:
            print(f"Waiting for RabbitMQ connection... (attempt {connection_attempts+1}/{max_attempts})")
            time.sleep(5)
            connection_attempts += 1
    raise Exception("Failed to connect to RabbitMQ")

def convert_image_of_bytes(image):
    return base64.b64encode(image)

def extract_frames_from_video():
    
    cap = cv2.VideoCapture("udp://127.0.0.1:5000")
    frame_count = 0
    start_time = time.time()
    channel = connect_rabbitmq()
    channel.queue_declare(queue='frame')


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

            conv_image = convert_image_of_bytes(frame)
            channel.basic_publish(exchange='',
                      routing_key='frame',
                      body=conv_image)
            print("[x] Sent message")

            #connection.close()
    cap.release()
    

if __name__ == "__main__":
    extract_frames_from_video()
