"""
Runner
Intended to be the entry point
use command line arguments/code flags to start an event processor/data listener/api process
"""
import json
import argparse
import time
import pandas as pd

from crisys.data_listener import DataListenerFactory
from crisys.event_processor import EventProcessorFactory

parser = argparse.ArgumentParser(
    prog='CriSys',
    description='A Crypto Risk Indicator',
    epilog='Made with ❤ at CMU'
)

if __name__ == '__main__':
    args = parser.parse_args()
    data_listener = DataListenerFactory.get_listener({}, listener_type='batch')
    price_event_processor = EventProcessorFactory.get_event_processor({}, processor_type='price')

    for data_type, raw_data in data_listener.start():

        processed_data = None
        if data_type == 'price':
            processed_data = price_event_processor.process(raw_data)
            print(pd.read_json(json.loads(processed_data), orient='columns'))
        elif data_type == 'news':
            ...
        time.sleep(5)

