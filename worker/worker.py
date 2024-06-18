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
    with open(f"output/{name_file}", "rb") as f:
       files = {"file": f} 
       url = "http://insightface-service:8000/data"
       response = requests.post(url, files=files)
       print(response.json()) 


def save_frame(frame_bytes, output_dir):
    try:
        file_name = f"frame_{len(os.listdir(output_dir)) + 1}.jpg"  # Используем индекс для уникального имени
        file_path = os.path.join(output_dir, file_name)

        image = Image.open(io.BytesIO(frame_bytes))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, image)
        #print(f"Сохранен кадр {file_name} в {file_path}")
        send_frame(file_name)
    except Exception as e:
        print(f"Ошибка обработки кадра: {e}")


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
