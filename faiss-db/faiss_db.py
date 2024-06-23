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
        vector = np.array(data["array"])
        return vector
    except Exception as e:
        print(f"Ошибка при получении векторов из сообщения: {e}")
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
                print(f"Вектор №{index.ntotal} добавлен.")
            else:
                print("Вектор не уникален, не добавляем.")
        except Exception as e:
            print(f"Ошибка при добавлении векторов в индекс Faiss: {e}")

def main():

    rabbit = KafkaBroker()
    rabbit.connect('kafka', 9092)
    try:
        rabbit.consume('faiss', callback)
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        rabbit.disconnect()
        sys.exit(0)


if __name__ == '__main__':
        main()