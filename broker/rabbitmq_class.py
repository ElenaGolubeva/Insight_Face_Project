from .broker_abstract import AbstractBrocker
import pika

class RabbitMQBroker(AbstractBrocker):
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self, host, port):
        # Подключение к RabbitMQ брокеру
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, connection_attempts=5, retry_delay=7))
                self.channel = self.connection.channel()
                print("Connected to RabbitMQ")
            except Exception as e:
                print(f"Failed to connect to RabbitMQ {e}")

    def publish(self, queue, message):
        self.channel.queue_declare(queue=queue)
        # Публикация сообщения в RabbitMQ
        self.channel.basic_publish(exchange='', routing_key=queue, body=message)

    def consume(self, queue, callback):
        # Получение сообщений из RabbitMQ
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def disconnect(self):
        # Отключение от RabbitMQ брокера
        self.connection.close()
