import os

import pandas as pd

pd.set_option('display.max_columns', None)

if __name__ == '__main__':
    # in minutes the resolution to aggregate the 5min BTCUSDT price data
    aggregate_to = 30
    filename = os.path.abspath(os.path.dirname(__file__)) + "/data/BTCUSDT-5m-combined.csv"
    df_5min = pd.read_csv(filename)
    df_5min = df_5min[['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    print('Input: ')
    print(df_5min.info())
    # some values in these columns are like 4567.89.1
    for col in ['High', 'Low', 'Close']:
        df_5min[col] = df_5min[col].apply(
            lambda x: float(x) if x.count('.') < 2 else float(x[:-2])
        )
    df_5min['OpenTime'] = pd.to_datetime(df_5min['OpenTime'], unit='ms')
    df_5min = df_5min.set_index('OpenTime')
    df_agg = df_5min.resample('30Min').agg({'Volume': 'sum',
                                            'High': 'max',
                                            'Low': 'min',
                                            'Open': lambda x: None if len(x) == 0 else x[0],
                                            'Close': lambda x: None if len(x) == 0 else x[-1]
                                            })
    df_agg = df_agg.dropna()
    df_agg = df_agg.reset_index(level=0)
    df_agg = df_agg.rename(mapper={
        'OpenTime': 'timestamp',
        'Volume': 'volume',
        'High': 'high',
        'Low': 'low',
        'Open': 'open',
        'Close': 'close'
    }, axis='columns')
    print('Processed: ')
    print(df_agg.info())
    print(df_agg.head())
    filename = os.path.abspath(os.path.dirname(__file__)) + "/data/" + str(aggregate_to) + "m_BTC_USD.csv"
    df_agg.to_csv(filename)
