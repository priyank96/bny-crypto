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
    print(df_5min.head())
    # some values in these columns are like 4567.89.1
    for col in ['High', 'Low', 'Close']:
        df_5min[col] = df_5min[col].apply(
            lambda x: float(x) if x.count('.') < 2 else float(x[:-2])
        )
    df_agg = []

    for i in range(0, len(df_5min), (aggregate_to // 5)):
        # opentime, open, high, low, close, volume
        if i + (aggregate_to // 5) - 1 >= len(df_5min):
            break
        row = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        row[0] = df_5min.iloc[i]['OpenTime']
        row[1] = df_5min.iloc[i]['Open']
        row[3] = df_5min.iloc[i]['Low']
        row[4] = df_5min.iloc[i + (aggregate_to // 5) - 1]['Close']
        for j in range(aggregate_to // 5):
            row[2] = max(row[2], df_5min.iloc[i + j]['High'])
            row[3] = min(row[3], df_5min.iloc[i + j]['Low'])
            row[5] += df_5min.iloc[i + j]['Volume']
        df_agg.append(row)
    df_agg = pd.DataFrame(df_agg, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # now the column names are per the processed data convention
    df_agg['timestamp'] = pd.to_datetime(df_agg['timestamp'], unit='ms')
    df_agg = df_agg.sort_values('timestamp', ascending=True)
    df_agg = df_agg.set_index('timestamp')

    print('Processed: ')
    print(df_agg.head())
    filename = os.path.abspath(os.path.dirname(__file__)) + "/data/"+str(aggregate_to)+"m_BTC_USD.csv"
    df_agg.to_csv(filename)
