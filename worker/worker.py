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
import socket

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
        #image_data = send_frame(file_name)
        return file_name

    except Exception as e:
        print(f"Error processing frame: {e}")


def main():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    broker_mess = KafkaBroker()
    broker_mess.connect()

    # TCP server setup
    TCP_IP = '0.0.0.0'
    TCP_PORT = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print(f'TCP server listening on {TCP_IP}:{TCP_PORT}')

    def callback(body):
        frame_name = save_frame(body, output_dir)
        image_data = send_frame(frame_name)
        if image_data:
            try:
                data_bytes = json.dumps({"face_vectors": image_data["face_vectors"]}).encode()
                broker_mess.publish('faiss', data_bytes)
            except Exception as e:
                print(f"Error publishing message to 'faiss' queue: {e}")

            try:
                conn, addr = s.accept()
                print('Connection address:', addr)
                
                try:
                    all_data_bytes = json.dumps({"image":image_data['image']}).encode()
                    conn.sendall(all_data_bytes)
                    print('Data sent to client')
                except Exception as e:
                    print(f"Error sending data through TCP: {e}")
                conn.close()

            except Exception as e:
                print(f"Error sending data through TCP: {e}")

    try:
        broker_mess.consume('frame', callback)
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        broker_mess.disconnect()
        s.close()
        sys.exit(0)

if __name__ == '__main__':
    main()