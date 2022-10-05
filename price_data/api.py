import os
import urllib.request
from pathlib import Path

import pandas as pd

API_KEY = '8X2HU0WTHV1BX717'
DAILY_DATA_URL = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=<symbol>&market=<market>&apikey=<api_key>&datatype=csv'  # nopep8


def read_price_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    return df


def fetch_new_daily_data(symbol: str):
    url = DAILY_DATA_URL
    url = url.replace('<api_key>', API_KEY) \
        .replace('<symbol>', symbol) \
        .replace('<market>', 'USD')
    urllib.request.urlretrieve(url, './temp.csv')
    data = read_price_csv('./temp.csv')
    data = data.rename(columns={"open (USD)": "open", "high (USD)": "high", "low (USD)": "low", "close (USD)": "close",
                                "market cap (USD)": "market cap"})
    data = data.drop(["open (USD).1", "high (USD).1", "low (USD).1", "close (USD).1"], axis=1)
    os.remove('temp.csv')
    return data


def update_daily_data(symbol: str):
    filename = os.path.abspath(os.path.dirname(__file__))+"/data/Daily_" + symbol + '_' + 'USD' + '.csv'
    new_data = fetch_new_daily_data(symbol)
    if Path(filename).is_file() is True:
        old_data = read_price_csv(filename)
        new_data = pd.concat([new_data, old_data]).groupby('timestamp').first()
        new_data = new_data.sort_values('timestamp', ascending=True)
    new_data.to_csv(filename)


def read_price_data(symbol: str, start_time, end_time, resolution='Daily'):
    if resolution == 'Daily':
        filename = os.path.abspath(os.path.dirname(__file__))+"/data/Daily_" + symbol + '_' + 'USD' + '.csv'
    else:
        print(f"{resolution} resolution is not currently supported!")
    df = pd.read_csv(filename)
    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    return df.loc[mask]


if __name__ == '__main__':
    update_daily_data('BTC')
    print(read_price_data('BTC', '2021-01-01', '2021-01-02'))
    update_daily_data('BTC')
    print(read_price_data('BTC', '2021-01-01', '2021-01-02'))
    update_daily_data('ETH')
    print(read_price_data('ETH', '2021-01-01', '2021-01-02').dtypes)
