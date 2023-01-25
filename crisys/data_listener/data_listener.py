"""
Data Listener Classes
Listen to the outside world and convert them to events to be written into Kafka
"""
import json
import time

from dateutil import parser
from datetime import timedelta
from price_data import read_price_data
from event_data import read_news_events
from crisys.util import get_kafka_producer


class BatchDataListener:
    def __init__(self, start_time, end_time, interval, price_data, news_data, social_data):
        self.price_data = price_data
        self.news_data = news_data
        self.social_data = social_data
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        # self.kafka_producer = get_kafka_producer()

    def start(self):
        dfs = [self.price_data, self.news_data]
        prev_time = self.start_time
        current_time = self.start_time + self.interval
        while prev_time <= self.end_time:
            prev_time = current_time
            current_time += self.interval
            for df in dfs:
                mask = (df['timestamp'] >= prev_time.strftime('%Y-%m-%dT%H:%M:%S%z')) & (
                        df['timestamp'] <= current_time.strftime('%Y-%m-%dT%H:%M:%S%z'))
                df = df.loc[mask]
                parsed_vals = self._jsonify(df)
                print(json.dumps(parsed_vals, indent=4))
                time.sleep(5)

    @staticmethod
    def _jsonify(df):
        df = df.set_index('timestamp')
        vals = df.to_json(orient='index')
        return json.loads(vals)



class DataListenerFactory:

    @staticmethod
    def get_listener(args, listener_type='batch'):
        if listener_type == 'batch':
            return DataListenerFactory._make_batch_data_listener(args)
        else:
            return None

    @staticmethod
    def _make_batch_data_listener(args):
        start_time = parser.isoparse('2021-01-01T00:00:00Z') if args.get('start_time') is None \
            else args.get('start_time')
        end_time = parser.isoparse('2023-01-01T00:00:00Z') if args.get('end_time') is None \
            else args.get('end_time')
        interval = timedelta(seconds=24 * 60 * 60) if args.get('interval') is None \
            else args.get('interval')
        symbol = 'BTC' if args.get('symbol') is None else args.get('symbol')

        price_data = read_price_data(symbol, start_time, end_time, interval.total_seconds())
        news_data = read_news_events(symbol, start_time, end_time)
        social_data = None

        return BatchDataListener(
            start_time,
            end_time,
            interval,
            price_data,
            news_data,
            social_data
        )
