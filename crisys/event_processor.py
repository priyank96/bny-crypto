"""
Event Processor Classes
read events coming from the data listener/other event processor,
apply transformations (calculate risk, do data cleaning etc.)
and output to kafka
"""
from util import get_kafka_consumer, get_kafka_producer
from config import KAFKA_DATA_LISTENER_OUT_TOPIC


class EventProcessorBase:
    """
    The event processor base class
    intended to be subclassed by risk event processors
    an event processor should work like:
    1. init - create class object
    2. start - this method will be called by the runner, to begin processing events
    3. process - each message read by the consumer will be processed by this function
    4. emit - to be called by the process function to serialize and emit the processed output
    """

    def __init__(self, topic):
        self.kafka_consumer = get_kafka_consumer(topic)
        self.kafka_producer = get_kafka_producer()

    def start(self):
        for message in self.kafka_consumer:
            self.process(message)

    def process(self, message):
        pass

    def emit(self, out):
        pass


class PriceRiskProcessor(EventProcessorBase):
    def __init__(self):
        super().__init__(KAFKA_DATA_LISTENER_OUT_TOPIC)

    def process(self, message):
        ...

    def emit(self, out):
        ...
