import os
from datetime import datetime

import pandas as pd
from price_data import read_price_data
from risk_measures import ZeroLagExpMovingAvg
from util import plot, plot_grid


def read_events(currency: str, kind: str):
    df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/' + currency + '_' + kind + '.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    return df


def read_tweet_counts(start_time, end_time):
    df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/tweet_counts.csv')
    df['date'] = pd.to_datetime(df['date'])
    print(df.info())
    df = df.set_index('date')
    df = df.sort_index()
    # Check this !!! what timezone is our tweet stuff coming back in?
    df.index = df.index.tz_localize(None)
    mask = (df.index >= start_time) & (df.index <= end_time)
    return df.loc[mask]


def read_news_events(currency, start_time, end_time):
    if currency == 'BTC':
        df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/BTC_coindesk_articles.csv', header=0,
                         sep='\t')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=True)
    elif currency == 'BTC_BERTopic':
        df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/article_class_probabilites.csv', header=0,
                         sep=',')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=True)
    if isinstance(start_time, datetime):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    if isinstance(end_time, datetime):
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S%z')

    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    return df.loc[mask]


class DashboardNewsData:
    topic_id_label_mapping = {
        -1: "Noise",
        0: "Companies",
        1: "Mining",
        2: "Adoption",  # Use of bitcoin as a currency
        3: "Price Behavior",
        4: "Coinbase",
        5: "Technology",
        6: "Companies",
        7: "Price Behavior",
        8: "Price Behavior",
        9: "Price Behavior",
        10: "Crime",
        11: "Other Crypto",
        12: "ETF",
        13: "Price Behavior",
        14: "Companies",
        15: "Regulatory",
        16: "Regulatory",
        17: "Regulatory",
        18: "Regulatory",
        19: "Price Behavior",
    }

    useful_topic_ids = {0, 1, 2, 4, 5, 6, 10, 12, 14, 15, 16, 17, 18}

    sentiment_index_label_mapping = {
        0: 'Negative',
        1: 'Neutral',
        2: 'Positive'
    }

    @staticmethod
    def dashboard_news_articles_to_show(currency, start_time, end_time):
        df = DashboardNewsData._load_news_df(currency, start_time, end_time)
        if len(df) == 0:
            df.index = df['timestamp']
            del df['sponsored']
            del df['labels']
            del df['timestamp']
            return df
        # filter useless articles
        df = df[(df['class_labels'].apply(lambda x: x[0] in DashboardNewsData.useful_topic_ids))]
        df['class_labels'] = df['class_labels'].apply(lambda x: DashboardNewsData.topic_id_label_mapping[x[0]])

        df['sentiment_logits'] = df['sentiment_logits'].apply(
            lambda x: DashboardNewsData.sentiment_index_label_mapping[x.index(max(x))])
        df.index = df['timestamp']
        del df['sponsored']
        del df['labels']
        del df['timestamp']
        return df

    @staticmethod
    def dashboard_news_aggregated_sentiment(currency, start_time, end_time, freq='30min'):
        df = DashboardNewsData._load_news_df(currency, start_time, end_time)
        if len(df) == 0:
            df['sentiment'] = []
            return df
        # filter useless articles
        df = df[(df['class_labels'].apply(lambda x: x[0] in DashboardNewsData.useful_topic_ids))]
        df['sentiment_logits'] = df['sentiment_logits'].apply(
            lambda x: x[2] - x[0])  # difference between positive and negative sentiment logit
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=True)

        # put everything in 30 min buckets
        time_range_index = pd.date_range(start=start_time, end=end_time, freq=freq, tz='UTC')
        final_df = pd.DataFrame(index=time_range_index, columns=['sentiment'])
        final_df.fillna(0.0, inplace=True)

        timedelta = pd.Timedelta(freq)
        for i in range(len(final_df)):
            for j in range(len(df)):
                if final_df.index[i] < df.iloc[j]['timestamp'] < final_df.index[i] + timedelta:
                    final_df.iloc[i]['sentiment'] += df.iloc[j]['sentiment_logits']
        return final_df

    @staticmethod
    def _load_news_df(currency, start_time, end_time):
        if isinstance(start_time, datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
        if isinstance(end_time, datetime):
            end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S%z')

        if currency == 'BTC':
            df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/article_topic_and_sentiment.csv',
                             header=0,
                             sep=',')
            df['class_labels'] = df['class_labels'].apply(lambda x: [int(val) for val in x[1:-1].split(',')])
            df['sentiment_logits'] = df['sentiment_logits'].apply(lambda x: [float(val) for val in x[1:-1].split(',')])

        mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
        return df.loc[mask]


if __name__ == '__main__':
    print(DashboardNewsData.dashboard_news_articles_to_show('BTC', '2021-01-14', '2021-01-15'))
    print(DashboardNewsData.dashboard_news_aggregated_sentiment('BTC', '2021-01-14', '2021-01-15'))
    # articles = read_news_events('BTC', '1921-01-01', '2025-07-01')
    # print(articles)
    # btc = read_price_data('BTC', '1921-01-01', '2025-07-01')
    # btc_tweets = read_tweet_counts('1921-01-01', '2025-07-01')
    # btc_events = read_events('BTC', 'Social')
    # to_plot = pd.DataFrame()
    # to_plot['timestamp'] = btc['timestamp']
    # to_plot['close'] = btc['close']
    # to_plot['volume'] = btc['volume']
    # # to_plot['Fib Pivot Point'] = FibonacciPivotPoints.calculate(btc)
    # to_plot['ZeroLagExpAvg'] = ZeroLagExpMovingAvg.calculate(btc)
    # to_plot['timestamp'] = pd.to_datetime(to_plot['timestamp'])
    # to_plot = to_plot.set_index('timestamp')
    # to_plot = to_plot.join(btc_tweets)
    # plot(to_plot, btc_events)
    # plot_grid(to_plot, btc_events)
