import os
import pandas as pd

from price_data import read_price_data
from risk_measures import ZeroLagExpMovingAvg, OBV, RSI, StochasticOscillator, Chaikin, AccumulationDistribution, MoneyFlowIndex,CommodityChannelIndex,EaseOfMovement,CoppockCurve
from util import plot


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
    # to_plot['close'] = btc['close']
    # to_plot['ZeroLagExpMvgAvg'] = ZeroLagExpMovingAvg.calculate(btc, 26)
    # to_plot['OBV'] = OBV.calculate(btc)
    # to_plot['rsi'] = RSI.calculate(btc)
    # to_plot['stochastic_oscillator'], _ = StochasticOscillator.calculate(btc)
    to_plot['chaikin'] = Chaikin.calculate(btc)
    # to_plot['accumulation_distribution'] = AccumulationDistribution.calculate(btc)
    # to_plot['money_flow_index'] = MoneyFlowIndex.calculate(btc)
    # to_plot['commodity_chanel_index'] = CommodityChannelIndex.calculate(btc)
    # to_plot['ease_of_movement'] = EaseOfMovement.calculate(btc, 14)
    # to_plot['coppock_curve'] = CoppockCurve.calculate(btc)
    to_plot['timestamp'] = pd.to_datetime(to_plot['timestamp'])
    to_plot = to_plot.set_index('timestamp')
    plot(to_plot, btc_events)
