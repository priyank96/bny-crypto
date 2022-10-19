import os
import pandas as pd

from price_data import read_price_data
from risk_measures import Volatility, RollingMDD, VaR, MACD, ROC
from util import plot_grid


def read_events(currency: str, kind: str):
    df = pd.read_csv(os.path.abspath(os.path.dirname(__file__))+'/data/'+currency+'_'+kind+'.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    return df


if __name__ == '__main__':
    btc = read_price_data('BTC', '1921-01-01', '2025-07-01')
    btc_events = read_events('BTC', 'Social')
    to_plot = pd.DataFrame()
    to_plot['timestamp'] = btc['timestamp']
    to_plot['close'] = btc['close']
    to_plot['ROC'] = ROC.calculate(btc)
    to_plot['volatility'] = Volatility.calculate(btc)
    to_plot['mdd'] = RollingMDD.calculate(btc)
    to_plot['var_90'] = VaR.calculate(btc, method=2)['var_90'].values
    to_plot['macd'] = MACD.calculate(btc)
    to_plot['timestamp'] = pd.to_datetime(to_plot['timestamp'])
    to_plot = to_plot.set_index('timestamp')
    plot_grid(to_plot, btc_events)
