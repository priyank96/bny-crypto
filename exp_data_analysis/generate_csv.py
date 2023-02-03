# from pycaret.regression import *
# from sklearn.metrics.pairwise import cosine_similarity 
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


# def cosine_similarity_custom(y, y_pred):
#     cs = cosine_similarity(np.array(y).reshape(1, -1), np.array(y_pred).reshape(1, -1))
#     return cs


if __name__ == '__main__':
    df = read_price_data('BTC', '2021-01-01', '2022-09-20', 30*60)
    btc_events = read_events('BTC', 'Social')

    values = pd.DataFrame()
    values['close'] = df['close']
    values['volume'] = df['volume']
    values['Awesome Oscillator'] = AwesomeOscillator.calculate(df)
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
    values['Forward MDD'] = ForwardRollingMDD.calculate(df)

    values['timestamp'] = df['timestamp']
    values['timestamp'] = pd.to_datetime(values['timestamp'])

    values = values.set_index('timestamp')

    values = values.iloc[40:-12, :]

    x = pd.DataFrame(values)
    x.to_csv("new_values.csv")
    # del x['Forward MDD']
    # train_split = int(0.7 * len(x))
    # x_train = x[:train_split]
    # x_test = x[train_split:]

    # s = setup(data = x_train, target = 'Forward MDD',test_data = x_test, fold_strategy = 'timeseries')
    # add_metric('distance', 'Cosine Distance', cosine_similarity_custom)
    # best = compare_models(sort='Cosine Distance')
    # print("Evaluate Model: ", evaluate_model(best))

    # predictions = predict_model(best, data=x_test)
    # print(predictions.head())
    # print("Cosine Similarity of Test Data: ", cosine_similarity_custom(predictions['Forward MDD'], predictions.Label))