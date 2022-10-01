import os
from pathlib import Path
import pandas as pd
import urllib.request

API_KEY = '8X2HU0WTHV1BX717'
DAILY_DATA_URL = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=<symbol>&market=<market>&apikey=<api_key>&datatype=csv'  # nopep8


def read_price_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def update_daily_data(symbol: str, currency='USD'):
    filename = './data/'+symbol+'_'+currency+'.csv'
    url = DAILY_DATA_URL
    url = url.replace('<api_key>', API_KEY)\
        .replace('<symbol>', symbol)\
        .replace('<market>', currency)
    if Path(filename).is_file() is not True:
        urllib.request.urlretrieve(url, filename)
    else:
        old_data = read_price_csv(filename)

        urllib.request.urlretrieve(url, filename+'_temp')
        new_data = read_price_csv(filename + '_temp')
        updated_data = pd.concat([new_data, old_data]).groupby('timestamp').first()

        updated_data = updated_data.sort_values('timestamp', ascending=False)
        updated_data.to_csv(filename)
        os.remove(filename+'_temp')
        print(updated_data.index.dtype)


if __name__ == '__main__':
    # tests
    update_daily_data('ETH')
    update_daily_data('BTC')