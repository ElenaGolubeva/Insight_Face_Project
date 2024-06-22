from .broker_abstract import AbstractBrocker


class KafkaBroker(AbstractBrocker):
    def __init__(self):

    def connect(self, host, port):

    def publish(self, topic, message):

    def consume(self, topic, callback):

    def disconnect(self):
