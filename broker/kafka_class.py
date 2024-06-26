from kafka import KafkaProducer, KafkaConsumer
from .broker_abstract import AbstractBrocker
import time
class KafkaBroker(AbstractBrocker):
    def __init__(self):
        self.producer = None
        self.consumer = None

    def connect(self):
        connection_attempts = 5
        retry_delay = 7
        attempt = 0
        for attempt in range(connection_attempts):
            try:
                self.producer = KafkaProducer(bootstrap_servers=f"kafka:9092")
                self.consumer = KafkaConsumer(bootstrap_servers=f"kafka:9092")
                print("Connected to Kafka")
                return
            except Exception as e:
                print(f"Failed to connect to Kafka on attempt{e}")
                time.sleep(retry_delay)
                attempt += 1

    def publish(self, topic, message):
        try:
            self.producer.send(topic, message)
            self.producer.flush()
        except Exception as e:
            print(f"Failed to publish of message to Apache Kafka {e}")

    def consume(self, topic, callback):
        try:
            self.consumer.subscribe([topic])
            for message in self.consumer:
                callback(message.value)
        except Exception as e:
            print(f"Failed to consume of message to Apache Kafka {e}")

    def disconnect(self):
        try:
            self.producer.close()
            self.consumer.close()
        except Exception as e:
            print(f"Failed to disconnect to Apache Kafka {e}")
