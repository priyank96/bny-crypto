import numpy as np
import pandas as pd
import ta
from finta import TA
from scipy.stats import norm

from price_data import read_price_data
from util import plot_grid


class RollingMDD:
    """
    Maximum Drawdown
    Definition: A maximum drawdown (MDD) is the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained
    Formula: MDD = (Trough Value - Peak Value)/Peak Value
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window=25):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].rolling(window).max()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return -1 * rolling_drawdown


class VaR:
    """
    Value at Risk
    Definition: Value at risk (VaR) is a statistic that quantifies the extent of possible financial losses

    Calculation:
                Method 1 Hist Simulation: Sort daily returns and return corresponding percentiles
                Method 2 Variance Covariance: find mean and std dev of returns and return corresponding confidence level of VaR
    """

    @staticmethod
    def calculate_var_row(df: pd.DataFrame, method: int = 1):
        # from https://blog.quantinsti.com/calculating-value-at-risk-in-excel-python/
        df_temp = pd.DataFrame()
        df_temp["pct"] = df["close"].pct_change()
        if method == 1:
            sorted_returns = df_temp.sort_values("pct")['pct']
            var90 = sorted_returns.quantile(0.1)
            var95 = sorted_returns.quantile(0.05)
            var99 = sorted_returns.quantile(0.01)
            return {"var_90": [-1 * var90],
                    "var_95": [-1 * var95],
                    "var_99": [-1 * var99]}
        else:
            mean = np.mean(df_temp.pct)
            std = np.std(df_temp.pct)
            var90 = norm.ppf(0.1, mean, std)
            var95 = norm.ppf(0.05, mean, std)
            var99 = norm.ppf(0.01, mean, std)
            return {"var_90": [-1 * var90],
                    "var_95": [-1 * var95],
                    "var_99": [-1 * var99]}

    @staticmethod
    def calculate(df: pd.DataFrame, method: int = 1):
        return_df = pd.DataFrame()
        for i in range(len(df)):
            temp = VaR.calculate_var_row(df.iloc[:i], method)
            return_df = pd.concat([return_df, pd.DataFrame(temp)])
        return return_df


class Volatility:

    @staticmethod
    def calculate(df: pd.DataFrame, window=10):
        #  what is volatility? https://www.wallstreetmojo.com/volatility-formula/
        # Implementation: https://stackoverflow.com/a/52941348/5699807 ; https://stackoverflow.com/a/43284457/5699807
        return df['close'].rolling(window=window).std(ddof=0)


class RSI:

    @staticmethod
    def calculate(df: pd.DataFrame):
        return ta.momentum.rsi(df.close)


class StochasticOscillator:

    @staticmethod
    def calculate(df: pd.DataFrame):
        return ta.momentum.stoch(df.high, df.low, df.close), ta.momentum.stoch_signal(df.high, df.low, df.close)


class OBV:

    @staticmethod
    def calculate(df: pd.DataFrame):
        copy = df.copy()
        return (np.sign(copy['close'].diff()) * copy['volume']).fillna(0).cumsum()


class Chaikin:

    @staticmethod
    def calculate(df):
        """Calculate Chaikin Oscillator for given data.
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
        Chaikin = pd.Series(ad.ewm(span=3, min_periods=3).mean() - ad.ewm(span=10, min_periods=10).mean(),
                            name='Chaikin')
        # df = df.join(Chaikin)
        return Chaikin


class AccumulationDistribution:

    @staticmethod
    def calculate(df):
        """Calculate Accumulation/Distribution for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """

        return TA.ADL(df)


class MACD:

    @staticmethod
    def calculate(df: pd.DataFrame, slow_long_window=26, slow_short_window=12, signal_window=9):
        slow_long = df['close'].ewm(span=slow_long_window, adjust=False, min_periods=slow_long_window).mean()
        slow_short = df['close'].ewm(span=slow_short_window, adjust=False, min_periods=slow_short_window).mean()
        MACD = slow_short - slow_long
        signal = MACD.ewm(span=signal_window, adjust=False, min_periods=signal_window).mean()
        trigger = MACD - signal
        return trigger


class MoneyFlowIndex:

    @staticmethod
    def calculate(df):
        # return ta.volume.MFIIndicator(df['high'],df['low'],df['close'],df['volume'],n)
        return TA.MFI(df)


class EaseOfMovement:

    @staticmethod
    def calculate(df, n):
        """Calculate Ease of Movement for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        EoM = (df['high'].diff(1) + df['low'].diff(1)) * (df['high'] - df['low']) / (2 * df['volume'])
        Eom_ma = pd.Series(EoM.rolling(n, min_periods=n).mean(), name='EoM_' + str(n))
        return Eom_ma


class CommodityChannelIndex:

    @staticmethod
    def calculate(df):
        """Calculate Commodity Channel Index for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        # PP = (df['high'] + df['low'] + df['close']) / 3
        # CCI = pd.Series((PP - PP.rolling(n, min_periods=n).mean()) / PP.rolling(n, min_periods=n).std(),
        #                 name='CCI_' + str(n))
        # return CCI
        return TA.CCI(df)


class CoppockCurve:

    @staticmethod
    def calculate(df):
        """Calculate Coppock Curve for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        return TA.COPP(df)


class ROC:
    """
    Rate of Change
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 1):
        M = df['close'].diff(n - 1)
        N = df['close'].shift(n - 1)
        ROC = pd.Series(M / N)
        return ROC


class TRIMA:
    """
    Triple Exponential Moving Average    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 18):
        return TA.TRIMA(df, n)


class VWAP:
    """
    Volume Weighted Average Price    
    """

    @staticmethod
    def calculate(df: pd.DataFrame):
        return TA.VWAP(df)


class ER:
    """
    Kaufman Efficiency Indicator
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 10):
        return TA.ER(df, n)


class TRIX:
    """
    Trix    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 20):
        return TA.TRIX(df, n)


class Qstick:
    """
    Quickstick    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 14):
        return TA.QSTICK(df, n)


class EFI:
    """
    Elder's Force Index    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 13):
        return TA.EFI(df, n)


class FISH:
    """
    Fisher Transform    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 13):
        return TA.FISH(df, n)


class CMO:
    """
    Chande Moving Oscillator    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, n: int = 9, factor: int = 100):
        return TA.CMO(df, n, factor)


class KAMA:
    """
    Kaufman's adaptive moving average    
    """

    @staticmethod
    def calculate(df: pd.DataFrame, er: int = 10, ema_fast: int = 2, ema_slow: int = 30, period: int = 20):
        return TA.KAMA(df, er, ema_fast, ema_slow, period)


class AverageTrueRange:
    """
    Average True Range:
    The indicator provide an indication of the degree of price volatility.
    Strong moves, in either direction, are often accompanied by large ranges, or large True Ranges.
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window=14):
        atr = ta.volatility.AverageTrueRange(high=df.high, low=df.low, close=df.close, window=window)
        return atr.average_true_range()


class UlcerIndex:
    """
    Ulcer Index:
    https://school.stockcharts.com/doku.php?id=technical_indicators:ulcer_index
    concerned with measuring maximum drawdown
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window: int = 14):
        ui = ta.volatility.UlcerIndex(close=df.close, window=window)
        return ui.ulcer_index()


class NegativeVolumeIndex:
    """
    Negative Volume Index Indicator
    https://school.stockcharts.com/doku.php?id=technical_indicators:negative_volume_inde
    The Negative Volume Index (NVI) is a cumulative indicator that uses the change in volume to decide
    when the smart money is active.
    Paul Dysart first developed this indicator in the 1930s.
    Dysart's Negative Volume Index works under the assumption that the smart money is active on days when
    volume decreases and the not-so-smart money is active on days when volume increases.
    """

    @staticmethod
    def calculate(df: pd.DataFrame):
        nvi = ta.volume.NegativeVolumeIndexIndicator(close=df.close, volume=df.volume)
        return nvi.negative_volume_index()


class ADX:
    """
    Average Directional Movement Index (ADX)
    https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window: int = 14):
        adx = ta.trend.ADXIndicator(high=df.high, low=df.low, close=df.close, window=window)
        return adx.adx()


class AroonIndicator:
    """
    Aroon Indicator
    Identify when trends are likely to change direction.
    Aroon Up = ((N - Days Since N-day High) / N) x 100
    Aroon Down = ((N - Days Since N-day Low) / N) x 100
    Aroon Indicator = Aroon Up - Aroon Down
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window: int = 25):
        ai = ta.trend.AroonIndicator(close=df.close, window=window)
        return ai.aroon_indicator()


class DPOI:
    """
    Detrend Price Oscillator:
    Is an indicator designed to remove trend from price and make it easier to identify cycles.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:detrended_price_osci
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window: int = 20):
        dpoi = ta.trend.DPOIndicator(close=df.close, window=window)
        return dpoi.dpo()


class MassIndex:
    """
    Mass Index (MI)
    It uses the high-low range to identify trend reversals based on range expansions.
    It identifies range bulges that can foreshadow a reversal of the current trend.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:mass_index
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window_fast: int = 9, window_slow: int = 25):
        mi = ta.trend.MassIndex(high=df.high, low=df.low, window_fast=window_fast, window_slow=window_slow)
        return mi.mass_index()


class VortexIndicator:
    """
    Vortex Indicator
    It consists of two oscillators that capture positive and negative trend movement.
    A bullish signal triggers when the positive trend indicator crosses above the negative trend indicator or a key level.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vortex_indicator
    """

    @staticmethod
    def calculate(df, window: int = 14):
        vi = ta.trend.VortexIndicator(high=df.high, low=df.low, close=df.close, window=window)
        return vi.vortex_indicator_diff()


class AwesomeOscillator:
    """
    Awesome Oscillator
    From: https://www.tradingview.com/wiki/Awesome_Oscillator_(AO)
    The Awesome Oscillator is an indicator used to measure market momentum.
    AO calculates the difference of a 34 Period and 5 Period Simple Moving Averages.
    The Simple Moving Averages that are used are not calculated using closing price but rather each bar’s midpoints.
    AO is generally used to affirm trends or to anticipate possible reversals.
    """

    @staticmethod
    def calculate(df, window1: int = 5, window2: int = 34):
        ao = ta.momentum.AwesomeOscillatorIndicator(high=df.high, low=df.low, window1=window1, window2=window2)
        return ao.awesome_oscillator()


if __name__ == '__main__':
    df = read_price_data('ETH', '2021-01-01', '2022-09-20', 'Daily')
    values = pd.DataFrame()
    values['close'] = df['close']
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
    values['Qstick'] = Qstick.calculate(df, 5)
    values['EFI'] = EFI.calculate(df)
    values['FISH'] = FISH.calculate(df)
    values['CMO'] = CMO.calculate(df)
    values['KAMA'] = KAMA.calculate(df)

    values['var_90'] = VaR.calculate(df, 1).var_90.values
    values['timestamp'] = df['timestamp']
    values['timestamp'] = pd.to_datetime(values['timestamp'])
    values = values.set_index('timestamp')
    plot_grid(values)
