import os
import pandas as pd

from price_data import read_price_data
from risk_measures import ZeroLagExpMovingAvg, Volatility, FibonacciPivotPoints
from util import plot, plot_grid


def read_events(currency: str, kind: str):
    df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/data/' + currency + '_' + kind + '.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    return df


if __name__ == '__main__':
    btc = read_price_data('BTC', '1921-01-01', '2025-07-01')
    btc_events = read_events('BTC', 'Social')
    to_plot = pd.DataFrame()
    to_plot['timestamp'] = btc['timestamp']
    to_plot['close'] = btc['close']
    # to_plot['Fib Pivot Point'] = FibonacciPivotPoints.calculate(btc)
    to_plot['ZeroLagExpAvg'] = ZeroLagExpMovingAvg.calculate(btc)
    to_plot['timestamp'] = pd.to_datetime(to_plot['timestamp'])
    to_plot = to_plot.set_index('timestamp')
    plot(to_plot, btc_events)
    plot_grid(to_plot, btc_events)
