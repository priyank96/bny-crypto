"""
Data Listener Classes
Listen to the outside world and convert them to events to be written into Kafka
"""
from datetime import datetime, timedelta
from price_data import read_price_data


class BatchDataListener:
    def __init__(self, start_time, end_time, interval, price_data, news_data, social_data):
        self.price_data = price_data
        self.news_data = news_data
        self.social_data = social_data
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval

    def start(self):
        ...


class DataListenerFactory:

    @staticmethod
    def get_listener(args, listener_type='batch'):
        if listener_type == 'batch':
            return DataListenerFactory._make_batch_data_listener(args)
        else:
            return None

    @staticmethod
    def _make_batch_data_listener(args):
        start_time = datetime.fromisoformat('2021-03-01T00:00:00Z') if args.get('start_time') is None \
            else args.get('start_time')
        end_time = datetime.fromisoformat('2023-01-01T00:00:00Z') if args.get('end_time') is None \
            else args.get('end_time')
        interval = timedelta(seconds=30 * 60) if args.get('interval') is None \
            else args.get('interval')
        symbol = 'BTC' if args.get('symbol') is None else args.get('symbol')

        price_data = read_price_data(symbol, start_time, end_time, interval.seconds)
        news_data = None
        social_data = None

        return BatchDataListener(
            start_time,
            end_time,
            interval,
            price_data,
            news_data,
            social_data
        )
