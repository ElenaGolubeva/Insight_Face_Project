import pika
import sys
import os
from PIL import Image
import cv2
import time
import io
import numpy as np

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
            time.sleep(5)
            connection_attempts += 1
    raise Exception("Failed to connect to RabbitMQ")

import hashlib

def save_frame(frame_bytes, output_dir):
    try:
        frame_count = 1
        file_name = f"frame_{frame_count}.jpg"
        file_path = os.path.join(output_dir, file_name)

        # Проверка, что файл с таким же содержимым не существует
        while os.path.exists(file_path):
            frame_hash = hashlib.md5(frame_bytes).hexdigest()
            for existing_file in os.listdir(output_dir):
                existing_file_path = os.path.join(output_dir, existing_file)
                existing_file_hash = hashlib.md5(open(existing_file_path, 'rb').read()).hexdigest()
                if frame_hash == existing_file_hash:
                    print(f"Frame {frame_count} is a duplicate, skipping.")
                    return
            frame_count += 1
            file_name = f"frame_{frame_count}.jpg"
            file_path = os.path.join(output_dir, file_name)

        image = Image.open(io.BytesIO(frame_bytes))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, image)
        print(f"Saved frame {frame_count} to {file_path}")
    except Exception as e:
        print(f"Error saving frame: {e}")


def main():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    channel, connection = connect_rabbitmq()
    channel.queue_declare(queue='frame')

    def callback(ch, method, properties, body):
        save_frame(body, output_dir)

    try:
        channel.basic_consume(queue='frame', on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        connection.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
