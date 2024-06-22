import json
import sys
import os
from PIL import Image
import cv2
import io
import numpy as np
import requests
from broker.rabbitmq_class import RabbitMQBroker
from broker.kafka_class import KafkaBroker

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
        file_name = f"frame_{len(os.listdir(output_dir)) + 1}.jpg"
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

    rabbit = RabbitMQBroker()
    rabbit.connect('rabbitmq', 5672)
    def callback(ch, method, properties, body):
        image_data = save_frame(body, output_dir)
        if image_data:
            try:
                list_in_dict = {'array': image_data['face_vectors']}
                data_bytes = json.dumps(list_in_dict).encode()
                rabbit.publish('faiss', data_bytes)
            except Exception as e:
                print(f"Error publishing message to 'faiss' queue: {e}")
    try:
        rabbit.consume('frame', callback)
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        rabbit.disconnect()
        sys.exit(0)

if __name__ == '__main__':
    main()