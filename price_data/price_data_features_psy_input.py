# Write PSY bubble prediction algorithm in python

import numpy as np
from statsmodels.tsa.stattools import adfuller
from tqdm import tqdm
import pandas as pd
import sys


def PSY(y, swindow0=None, IC=0, adflag=0):

    t = len(y)

    if swindow0 is None:
        swindow0 = int(np.floor(t * (0.01 + 1.8 / np.sqrt(t))))

    bsadfs = np.empty(t)
    bsadfs[:] = np.nan

    for r2 in tqdm(range(swindow0, t)):
        rwadft = np.empty(r2 - swindow0 + 1)
        rwadft[:] = -999
        for r1 in range(0, r2 - swindow0 + 1):
            rwadft[r1] = adfuller(y[r1:r2+1], maxlag=adflag, autolag=None)[0]

        bsadfs[r2] = np.max(rwadft)

    bsadf = np.hstack((np.zeros(swindow0), bsadfs[swindow0:t]))

    return bsadf

if __name__ == '__main__':

    price_data_df = pd.read_csv('data/30m_BTC_USD.csv')
    # price_data_df.drop(columns=['Unnamed: 0'], inplace=True)
    # Take first 100 rows
    # start, length = 10000, 5000
    # price_data_df = price_data_df.iloc[start:start+length]

    basetime = 0.5 # 0.5 hours or 30 mins
    # timeperiod_list = ['3h', '6h', '12h', '1d', '3d', '7d']
    timeperiod = sys.argv[1]
    print(f"Time period: {timeperiod}")
    if f'PSY_{timeperiod}' not in price_data_df.columns:
        if timeperiod[-1] == 'h':
            window = int(timeperiod[:-1]) * 2
        elif timeperiod[-1] == 'd':
            window = int(timeperiod[:-1]) * 2 * 24
        price_data_df[f'PSY_{timeperiod}'] = PSY(price_data_df['close'].values, swindow0=window, IC=0, adflag=0)

    price_data_df.to_csv(f'data/30m_BTC_USD_PSY_{timeperiod}.csv', index=False)
