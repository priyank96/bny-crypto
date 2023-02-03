import csv
import time

import pandas as pd
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# API_KEY = '8X2HU0WTHV1BX717'
# CSV_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=SPY&interval=30min&slice=<slice>&apikey=8X2HU0WTHV1BX717'
#
# slices = []
# for i in [1, 2]:
#     for j in range(1, 13):
#         slices.append(f'year{i}month{j}')
#
# rows = []
# with requests.Session() as s:
#     for slice in slices:
#         download = s.get(CSV_URL.replace("<slice>", slice))
#         decoded_content = download.content.decode('utf-8')
#         cr = csv.reader(decoded_content.splitlines(), delimiter=',')
#         next(cr)
#         rows.extend(list(cr))
#         time.sleep(60)
# df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
# df = df.sort_values('timestamp', ascending=True)
# print(df.head())
# df.to_csv('sp500.csv')

df = pd.read_csv('values.csv', header=0)
spdf = pd.read_csv('sp500.csv', header=0)

del spdf["high"]
del spdf["low"]
del spdf["open"]

spdf.rename(mapper={
    "close": "SPY_Close",
    "volume": "SPY_Volume",
    "timestamp": "SPY_timestamp"
}, axis='columns', inplace=True)
# print(df.info())
print(spdf.info())
df = pd.merge(df, spdf, left_on='timestamp', right_on='SPY_timestamp')
del df["SPY_timestamp"]
print(df.info())
df.to_csv('sp500values.csv', index=False)
