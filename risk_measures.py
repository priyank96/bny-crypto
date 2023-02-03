import numpy as np
import pandas as pd
import ta
from finta import TA
from scipy.stats import norm

from price_data import read_price_data
from util import plot_grid

import requests
from datetime import datetime


class ForwardRollingMDD:

    @staticmethod
    # def calculate(df: pd.DataFrame, window=12):
    #     # reverse the column, get the rolling min
    #     roll_min = df['close'][::-1].rolling(window).min()
    #     rolling_drawdown = -1 * (roll_min / df['close'] - 1.0)
    #     return rolling_drawdown
    
    def calculate(df, window=12):
        """
        fmdd is defined as the forward maximum drawdown
        (considering open prices)
        arg:
            df = dataframe with the 30min data
        output:
            dataframe with 6 hour fmdd added as a column
        """
        temp_list = []

        df = df[["close"]]
        for i in range(len(df)-window):
            forward_df = df.iloc[i:i+window]
            max_idx = forward_df.idxmax("index")
            max = forward_df.loc[max_idx].close.iloc[0]
            forward_df = forward_df.loc[max_idx[0]:]
            min = forward_df.min("index")[0]
            mdd = (max-min)/max
            temp_list.append(mdd)
        for i in range(window):
            temp_list.append(0)

        return temp_list    


class RollingMDD:
    """
    Maximum Drawdown
    Definition: A maximum drawdown (MDD) is the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained
    Formula: MDD = (Trough Value - Peak Value)/Peak Value
    """

    @staticmethod
    def calculate(df: pd.DataFrame, window=12):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].rolling(window).max()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return -1 * rolling_drawdown
    

    # def calculate(df: pd.DataFrame, window=12):
    # #  from https://quant.stackexchange.com/a/45407
    #     roll_max = df['close'].rolling(window).max()
    #     rolling_drawdown = df['close'] / roll_max - 1.0
    #     Max_Daily_Drawdown = rolling_drawdown.rolling(window, min_periods=1).min()

    #     return Max_Daily_Drawdown


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
    def calculate(df, n=14):
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


class PivotPoints:
    """
    Pivot Point
    A pivot point is a technical analysis indicator, or calculations, used to determine the overall trend of the market 
    over different time frames. The pivot point itself is simply the average of the intraday high and low, and the closing
    price from the previous trading day. On the subsequent day, trading above the pivot point is thought to indicate ongoing 
    bullish sentiment, while trading below the pivot point indicates bearish sentiment.
    """

    @staticmethod
    def calculate(df):
        return TA.PIVOT(df)['pivot']


class FibonacciPivotPoints:
    """
    Fibonacci Pivot Points(https://www.babypips.com/learn/forex/other-pivot-point-calculation-methods)

    Fibonacci pivot point levels are determined by first calculating the pivot point like you would the standard method.
    Next, multiply the previous day’s range with its corresponding Fibonacci level. Most traders use the 38.2%, 61.8% and 100% retracements in their calculations.
    Finally, add or subtract the figures you get to the pivot point and voila, you’ve got your Fibonacci pivot point levels!
    """

    @staticmethod
    def calculate(df):
        return TA.PIVOT_FIB(df)['pivot']


class MomentumBreakoutBands:
    """
    Momentum Breakout Bands

    These bands are bollinger bands that have an adjusted standard deviation. There are Buy signals when it has momentum breakouts above 
    the bands for moves to the upside and Sell signals when it has momentum breakouts below the bands for moves to the downside.
    """

    @staticmethod
    def calculate(df):
        return TA.MOBO(df)["BB_MIDDLE"]


class KeltnerChannels:
    """
    Keltner Channels

    Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a trend
    """

    @staticmethod
    def calculate(df):
        return TA.KC(df)["KC_UPPER"]


class TrueStrengthIndex:
    """
    True Strength Indicator
    """

    @staticmethod
    def calculate(df):
        return TA.TSI(df)["TSI"]


class HullMovingAvg:
    """
    Hull Moving Average
    """

    @staticmethod
    def calculate(df):
        return TA.HMA(df)


class ZeroLagExpMovingAvg:

    @staticmethod
    def calculate(df, period: int = 26):
        return TA.ZLEMA(df, period=period)


class InverseFisherTransformRSI:

    @staticmethod
    def calculate(df):
        return TA.IFT_RSI(df)


class Chandelier:
    """
    Chandelier Exit (CE) is a volatility-based indicator that identifies stop loss exit points for long and short trading positions. 
    Chandelier Exit Long: n-day Highest High – ATR (n) x Multiplier
    Chandelier Exit Short: n-day Lowest Low + ATR (n) x Multiplier
    Where:
    N is the default unit period of 22 or the number that the trader chooses.
    The multiplier is the default 3.0 Average True Range.
    """

    @staticmethod
    def calculate(df):  # short_period: int = 22, long_period: int = 22, k: int = 3,
        return TA.CHANDELIER(df)


class Williams:
    """
    Williams %R, or just %R, is a technical analysis oscillator showing the current closing price in relation to the high and low
    of the past N days (for a given N). It was developed by a publisher and promoter of trading materials, Larry Williams.
    Its purpose is to tell whether a stock or commodity market is trading near the high or the low, or somewhere in between,
    of its recent trading range.
    The oscillator is on a negative scale, from −100 (lowest) up to 0 (highest).
    """

    @staticmethod
    def calculate(df):  # period: int = 14
        return TA.WILLIAMS(df)


class Williams_Fractal_Indicator:
    """
    Williams Fractal Indicator
    Source: https://www.investopedia.com/terms/f/fractal.asp
    :param DataFrame ohlc: data
    :param int period: how many lower highs/higher lows the extremum value should be preceded and followed.
    :return DataFrame: fractals identified by boolean
    """

    @staticmethod
    def calculate(df):  # period: int = 2
        return TA.WILLIAMS_FRACTAL(df)


class VolumeZoneOscillator:
    """VZO uses price, previous price and moving averages to compute its oscillating value.
    It is a leading indicator that calculates buy and sell signals based on oversold / overbought conditions.
    Oscillations between the 5% and 40% levels mark a bullish trend zone, while oscillations between -40% and 5% mark a bearish trend zone.
    Meanwhile, readings above 40% signal an overbought condition, while readings above 60% signal an extremely overbought condition.
    Alternatively, readings below -40% indicate an oversold condition, which becomes extremely oversold below -60%."""

    @staticmethod
    def calculate(df):  # period: int = 14, column: str = "close", adjust: bool = True,
        return TA.VZO(df)


class VolumePriceTrend:
    """
    Volume Price Trend
    The Volume Price Trend uses the difference of price and previous price with volume and feedback to arrive at its final form.
    If there appears to be a bullish divergence of price and the VPT (upward slope of the VPT and downward slope of the price) a buy opportunity exists.
    Conversely, a bearish divergence (downward slope of the VPT and upward slope of the price) implies a sell opportunity.
    """

    @staticmethod
    def calculate(df):
        return TA.VPT(df)


class FiniteVolumeElement:
    """
    FVE is a technical indicator, but it has two important innovations: first, the F VE takes into account both intra and
    interday price action, and second, minimal price changes are taken into account by introducing a price threshold.
    """

    @staticmethod
    def calculate(df):  # period: int = 22, factor: int = 0.3
        return TA.FVE(df)


class StochRSI:
    """StochRSI is an oscillator that measures the level of RSI relative to its high-low range over a set time period.
    StochRSI applies the Stochastics formula to RSI values, instead of price values. This makes it an indicator of an indicator.
    The result is an oscillator that fluctuates between 0 and 1."""

    @staticmethod
    def calculate(df):  # rsi_period: int = 14, stoch_period: int = 14
        return TA.STOCHRSI(df)


class SAR:
    """SAR stands for “stop and reverse,” which is the actual indicator used in the system.
    SAR trails price as the trend extends over time. The indicator is below prices when prices are rising and above prices when prices are falling.
    In this regard, the indicator stops and reverses when the price trend reverses and breaks above or below the indicator."""

    @staticmethod
    def calculate(df):  # af: int = 0.02, amax: int = 0.2
        return TA.SAR(df)


class BASPN:
    """
    Normalized BASP indicator
    """

    @staticmethod
    def calculate(df):  # period: int = 40, adjust: bool = True
        return TA.BASPN(df)


class BBANDS:
    """
    Bollinger Bands
    """

    @staticmethod
    def calculate(df):  # period: int = 40, adjust: bool = True
        return TA.BBANDS(df)


class FearOrGreed:
    """
    Ref API: https://alternative.me/crypto/fear-and-greed-index/
    """

    def __init__(self):
        self.data = requests.get('https://api.alternative.me/fng/?limit=0&date_format=us').json()['data']

    def calculate(self, df):

        ret_list = list()
        for i in range(len(df)):
            df_date = datetime.strptime(df.iloc[i]['timestamp'], '%Y-%m-%d')
            for d in self.data:
                if datetime.strptime(d['timestamp'], '%m-%d-%Y') == df_date:
                    ret_list.append(d['value'])
        return ret_list


class ICHIMOKU:
    """
    ICHIMOKU Cloud
    """

    @staticmethod
    def calculate(df):  # period: int = 40, adjust: bool = True
        return TA.ICHIMOKU(df)


def StandardDeviation(df, n):
    """Calculate Standard Deviation for given data.
    
    :param df: pandas.DataFrame
    :param n: 
    :return: pandas.DataFrame
    """
    return df['close'].rolling(n, min_periods=n).std()


if __name__ == '__main__':
    df = read_price_data('ETH', '2021-01-01', '2022-09-20', 24 * 60 * 60)
    values = pd.DataFrame()
    values['close'] = df['close']
    values['volume'] = df['volume']
    values['timestamp'] = pd.to_datetime(df['timestamp'])
    values['forward_MDD'] = ForwardRollingMDD.calculate(df)
    values = values.set_index('timestamp')

    plot_grid(values)
