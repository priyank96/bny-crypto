import pandas as pd

from price_data import read_price_data
from risk_measures import Volatility
from util import plot_grid

if __name__ == '__main__':
    btc = read_price_data('BTC', '2018-01-01', '2024-01-01')
    eth = read_price_data('BTC', '2018-01-01', '2024-01-01')

    to_plot = pd.DataFrame()
    to_plot['close'] = btc['close']
    to_plot['volatility'] = Volatility.calculate(btc)
    plot_grid(to_plot)
