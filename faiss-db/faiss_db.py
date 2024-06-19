import json
import numpy as np
import faiss
import pika, sys, os
import time


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

def get_vectors_from_message(body):
    try:
        data = json.loads(body.decode())
        vector = np.array(data["array"])
        return vector
    except Exception as e:
        print(f"Ошибка при получении векторов из сообщения: {e}")
        return None

def main():
    d = 512
    index = faiss.IndexFlat(d)
    channel, connection = connect_rabbitmq()
    channel.queue_declare(queue='faiss')

    def callback(ch, method, properties, body):
        vectors = get_vectors_from_message(body)
        if vectors is not None:
            try:
                index.add(vectors)
                print(f"Вектор №{index.ntotal} добавлен. ")
            except Exception as e:
                print(f"Ошибка при добавлении векторов в индекс Faiss: {e}")


    try:
        channel.basic_consume(queue='faiss', on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        connection.close()
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)