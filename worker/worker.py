import json
import pika
import sys
import os
from PIL import Image
import cv2
import time
import io
import numpy as np
import requests

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

def send_frame(name_file):
    try:
        with open(f"output/{name_file}", "rb") as f:
            files = {"file": f}
            url = "http://insightface-service:8000/data"
            response = requests.post(url, files=files)
            return response.json()
    except Exception as e:
        print(f"Error sending frame: {e}")
        return None


def save_frame(frame_bytes, output_dir):
    try:
        file_name = f"frame_{len(os.listdir(output_dir)) + 1}.jpg"  # Use index for unique name
        file_path = os.path.join(output_dir, file_name)

        image = Image.open(io.BytesIO(frame_bytes))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, image)
        image_data = send_frame(file_name)
        return image_data

    except Exception as e:
        print(f"Error processing frame: {e}")


def main():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    channel, connection = connect_rabbitmq()
    channel.queue_declare(queue='frame')
    channel.queue_declare(queue="faiss")

    def callback(ch, method, properties, body):
        image_data = save_frame(body, output_dir)
        if image_data:
            try:
                list_in_dict = {'array': image_data['face_vectors']}
                data_bytes = json.dumps(list_in_dict).encode()
                channel.basic_publish(exchange='',
                                     routing_key='faiss',
                                     body=data_bytes)
            except Exception as e:
                print(f"Error publishing message to 'faiss' queue: {e}")

    try:
        channel.basic_consume(queue='frame', on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        connection.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
