"""
Event Processor Classes
read events coming from the data listener/other event processor,
apply transformations (calculate risk, do data cleaning etc.)
and output to kafka
"""
import json
import pandas as pd

from crisys.util import jsonify, json_to_df


class EventProcessorBase:
    """
    The event processor base class
    intended to be subclassed by risk event processors
    an event processor should work like:
    1. init - create class object
    2. process - each message read by the consumer will be processed by this function
    """

    def __init__(self):
        pass

    def process(self, message):
        pass


class PriceRiskProcessor(EventProcessorBase):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def process(self, message):
        df = json_to_df(message)
        value = self.model(df)
        return jsonify(value)


class EventProcessorFactory:

    @staticmethod
    def get_event_processor(args, processor_type):
        if processor_type == 'price':
            return PriceRiskProcessor(
                lambda x: x if args.get('model') is None else args['model']
            )
        return None
