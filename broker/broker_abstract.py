﻿from abc import ABC, abstractmethod

class AbstractBrocker(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def publish(self, topic, message):
        pass

    @abstractmethod
    def consume(self, topic, callback):
        pass

    @abstractmethod
    def disconnect(self):
        pass