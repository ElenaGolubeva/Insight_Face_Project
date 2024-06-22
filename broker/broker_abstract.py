from abc import ABC, abstractmethod

class AbstractBrocker(ABC):
    @abstractmethod
    def connect(self, host, port):
        pass

    @abstractmethod
    def publish(self, topic, message):
        pass

    @abstractmethod
    def consume(self, topic):
        pass

    @abstractmethod
    def disconnect(self):
        pass