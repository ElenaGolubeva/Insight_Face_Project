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

def unique_vector(f_index, b_vector):
    if b_vector is not None:
        try:
            distances, indices = f_index.search(np.expand_dims(b_vector, axis=0), 1)
            if distances[0][0] > 1e-6:
                return b_vector
        except Exception as e:
             print(f"Ошибка при определении уникальности вектора: {e}")
    return None
    
def callback(ch, method, properties, body):
        vector_from_body = get_vector(body)
        #vector = unique_vector(index, vector_from_body)
        if vector_from_body is not None:
            try:
                index.add(vector_from_body)
                print(f"Вектор №{index.ntotal} добавлен. ")
            except Exception as e:
                print(f"Ошибка при добавлении векторов в индекс Faiss: {e}")


def main():

    rabbit = RabbitMQBroker()
    rabbit.connect('rabbitmq', 5672)
    try:
        rabbit.consume('faiss', callback)
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        rabbit.disconnect()
        sys.exit(0)


if __name__ == '__main__':
        main()