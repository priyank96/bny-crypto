"""
Common utils
"""
from kafka import KafkaConsumer, KafkaProducer
from crisys.config import KAFKA_BOOTSTRAP_SERVER


def get_kafka_consumer(topic, group_id=None):
    return KafkaConsumer(topic, group_id=group_id)


__producer = None


def get_kafka_producer():
    global __producer
    if __producer is None:
        __producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER)
    return __producer
