import numpy as np
import pandas as pd
from scipy.stats import norm
from finta import TA


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


class MACD:

    @staticmethod
    def calculate(df: pd.DataFrame, slow_long_window=26, slow_short_window=12, signal_window=9):
        slow_long = df['close'].ewm(span=slow_long_window, adjust=False, min_periods=slow_long_window).mean()
        slow_short = df['close'].ewm(span=slow_short_window, adjust=False, min_periods=slow_short_window).mean()
        MACD = slow_short - slow_long
        signal = MACD.ewm(span=signal_window, adjust=False, min_periods=signal_window).mean()
        trigger = MACD - signal
        return trigger

class ROC:
    """
    Rate of Change
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 1):
        M = df['close'].diff(n-1)
        N = df['close'].shift(n-1)
        ROC = pd.Series(M/N)
        return ROC
        

class TRIMA:
    """
    Triple Exponential Moving Average    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 18):
        return TA.TRIMA(df,n)

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
    def calculate(df: pd.DataFrame,n:int = 10):
        return TA.ER(df,n)

class TRIX:
    """
    Trix    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 20):
        return TA.TRIX(df,n)

class Qstick:
    """
    Quickstick    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 14):
        return TA.QSTICK(df,n)

class EFI:
    """
    Elder's Force Index    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 13):
        return TA.EFI(df,n)

class FISH:
    """
    Fisher Transform    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 13):
        return TA.FISH(df,n)

class CMO:
    """
    Chande Moving Oscillator    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, n:int = 9,factor:int =100):
        return TA.CMO(df,n,factor)

class KAMA:
    """
    Kaufman's adaptive moving average    
    """
    @staticmethod
    def calculate(df: pd.DataFrame, er:int = 10,ema_fast:int =2, ema_slow:int=30, period:int = 20):
        return TA.KAMA(df,er,ema_fast,ema_slow,period)

if __name__ == '__main__':
    df = read_price_data('BTC', '2021-01-01', '2021-10-20', 'Daily')
    values = pd.DataFrame()
    values['close'] = df['close']
    values['volatility'] = Volatility.calculate(df)
    values['mdd'] = RollingMDD.calculate(df)
    values['MACD'] = MACD.calculate(df)
    values['ROC'] = ROC.calculate(df,1)
    values['TRIMA'] = TRIMA.calculate(df,1)
    values['TRIX'] = TRIX.calculate(df,1)
    values['VWAP'] = VWAP.calculate(df)
    values['ER'] = ER.calculate(df)
    values['Qstick'] = Qstick.calculate(df,5)
    values['EFI'] = EFI.calculate(df)
    values['FISH'] = FISH.calculate(df)
    values['CMO'] = CMO.calculate(df)
    values['KAMA'] = KAMA.calculate(df)




    values['var_90'] = VaR.calculate(df, 1).var_90.values
    values['timestamp'] = df['timestamp']
    values['timestamp'] = pd.to_datetime(values['timestamp'])
    values = values.set_index('timestamp')
    plot_grid(values)
