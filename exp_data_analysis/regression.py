import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

import sys
sys.path.append("..")

from util import plot_grid
from risk_measures import *
from event_data import read_events
from price_data import read_price_data
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error

if __name__ == '__main__':
    df = read_price_data('ETH', '2021-01-01', '2022-09-20', 'Daily')
    btc_events = read_events('BTC', 'Social')

    values = pd.DataFrame()
    values['close'] = df['close']
    values['volume'] = df['volume']
    values['Awesome Oscillator'] = AwesomeOscillator.calculate(df)
    values['Forward MDD'] = ForwardRollingMDD.calculate(df)
    values['Vortex Indicator'] = VortexIndicator.calculate(df)
    values['Mass Index'] = MassIndex.calculate(df)
    values['Detrend Price Oscillator'] = DPOI.calculate(df)
    values['Avg True Range'] = AverageTrueRange.calculate(df)
    values['Ulcer Index'] = UlcerIndex.calculate(df)
    values['Negative Volume Index'] = NegativeVolumeIndex.calculate(df)
    values['ADX'] = ADX.calculate(df)
    values['Aroon Indicator'] = AroonIndicator.calculate(df)
    values['volatility'] = Volatility.calculate(df)
    values['mdd'] = RollingMDD.calculate(df)
    values['OBV'] = OBV.calculate(df)
    values['rsi'] = RSI.calculate(df)
    values['stochastic_oscillator'], _ = StochasticOscillator.calculate(df)
    values['chaikin'] = Chaikin.calculate(df)
    values['accumulation_distribution'] = AccumulationDistribution.calculate(df)
    values['money_flow_index'] = MoneyFlowIndex.calculate(df)
    values['commodity_chanel_index'] = CommodityChannelIndex.calculate(df)
    values['ease_of_movement'] = EaseOfMovement.calculate(df, 1)
    values['coppock_curve'] = CoppockCurve.calculate(df)
    values['MACD'] = MACD.calculate(df)
    values['ROC'] = ROC.calculate(df, 1)
    values['TRIMA'] = TRIMA.calculate(df, 1)
    values['TRIX'] = TRIX.calculate(df, 1)
    values['VWAP'] = VWAP.calculate(df)
    values['ER'] = ER.calculate(df)
    # values['Qstick'] = Qstick.calculate(df, 5)
    values['EFI'] = EFI.calculate(df)
    values['FISH'] = FISH.calculate(df)
    values['CMO'] = CMO.calculate(df)
    values['KAMA'] = KAMA.calculate(df)

    values["PIVOT"] = PivotPoints.calculate(df)
    values["PIVOT_FIB"] = FibonacciPivotPoints.calculate(df)
    values["MOBO"] = MomentumBreakoutBands.calculate(df)
    values["KC"] = KeltnerChannels.calculate(df)
    values["TSI"] = TrueStrengthIndex.calculate(df)
    values["HMA"] = HullMovingAvg.calculate(df)
    values["ZLEMA"] = ZeroLagExpMovingAvg.calculate(df)
    values["IFT_RSI"] = InverseFisherTransformRSI.calculate(df)

    values['var_90'] = VaR.calculate(df, 1).var_90.values
    values['timestamp'] = df['timestamp']
    values['timestamp'] = pd.to_datetime(values['timestamp'])

    values = values.set_index('timestamp')
    values = values.iloc[40:-25, :]

    regressor = LinearRegression(normalize=True)
    x = pd.DataFrame(values)
    del x['Forward MDD']
    regressor.fit(x, values['Forward MDD'])
    pred = regressor.predict(x)
    print('Regression cosine distance: ',
        pairwise_distances(pred.reshape(1, -1), values['Forward MDD'].values.reshape(1, -1), metric='cosine'))
    model_repr = list(zip(x.columns, regressor.coef_))
    model_repr.sort(key=lambda x: abs(x[1]), reverse=True)
    for attrib, weight in model_repr:
        if weight != 0.0:
            print(attrib, weight)
    values['Linear Regression'] = pred
    plot_grid(values[['close', 'Forward MDD', 'Linear Regression']])