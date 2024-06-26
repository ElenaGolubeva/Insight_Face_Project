import json
import numpy as np
import faiss
import sys
from broker.rabbitmq_class import RabbitMQBroker
from broker.kafka_class import KafkaBroker

d = 512
index = faiss.IndexFlat(d)

def get_vector(body):
    try:
        data = json.loads(body.decode())
        vector = np.array(data["face_vectors"])
        return vector
    except Exception as e:
        print(f"Error receiving vectors from a message: {e}")
        return None

def is_unique_vector(vector):
    if index.ntotal == 0:
        return True
    distances, _ = index.search(vector.reshape(1, -1), 1)
    if distances[0, 0] < 1e-5:
        return False
    return True

def callback(body):
    vector_from_body = get_vector(body)
    if vector_from_body is not None:
        try:
            if is_unique_vector(vector_from_body):
                index.add(vector_from_body)
                print(f"Vector №{index.ntotal} added.")
        except Exception as e:
            print(f"Error when adding vectors to the Faiss index: {e}")

def main():

    mess_broker = KafkaBroker()
    mess_broker.connect()
    try:
        mess_broker.consume('faiss', callback)
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        mess_broker.disconnect()
        sys.exit(0)


if __name__ == '__main__':
        main()