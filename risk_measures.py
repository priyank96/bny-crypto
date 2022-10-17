import numpy as np
import pandas as pd
from scipy.stats import norm
import ta
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

class RSI: 
    def calculate(df: pd.DataFrame):
        return ta.momentum.rsi(df.close)

class Stochastic_Oscillator: 
    def calculate(df: pd.DataFrame):
        return ta.momentum.stoch(df.high, df.low, df.close), ta.momentum.stoch_signal(df.high, df.low, df.close)

class OBV:
    def calculate(df: pd.DataFrame):
        copy = df.copy()
        return (np.sign(copy['close'].diff())*copy['volume']).fillna(0).cumsum()

class Chaikin:
    def calculate(df):
        """Calculate Chaikin Oscillator for given data.
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
        Chaikin = pd.Series(ad.ewm(span=3, min_periods=3).mean() - ad.ewm(span=10, min_periods=10).mean(), name='Chaikin')
        # df = df.join(Chaikin)
        return Chaikin

class Accumulation_Distribution:
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

class Money_Flow_Index:
    def calculate(df):
        #return ta.volume.MFIIndicator(df['high'],df['low'],df['close'],df['volume'],n)
        return TA.MFI(df)

# class Money_Flow_Index:
#     def calculate(df, n=14):
#         typical_price = (df.high + df.low + df.close)/3
#         money_flow = typical_price * df.volume
#         mf_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
#         signed_mf = money_flow * mf_sign
#         mf_avg_gain = signed_mf.rolling(n).apply(gain, raw=True)
#         mf_avg_loss = signed_mf.rolling(n).apply(loss, raw=True)
#         return (100 - (100 / (1 + (mf_avg_gain / abs(mf_avg_loss))))).to_numpy()


class Ease_of_Movement:
    def calculate(df, n):
        """Calculate Ease of Movement for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        EoM = (df['high'].diff(1) + df['low'].diff(1)) * (df['high'] - df['low']) / (2 * df['volume'])
        Eom_ma = pd.Series(EoM.rolling(n, min_periods=n).mean(), name='EoM_' + str(n))
        return Eom_ma

class Commodity_Chanel_Index:
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

class Coppock_Curve:
    def calculate(df):
        """Calculate Coppock Curve for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        return TA.COPP(df)

if __name__ == '__main__':
    df = read_price_data('ETH', '2021-01-01', '2022-09-20', 'Daily')
    values = pd.DataFrame()
    # values['close'] = df['close']
    # values['volatility'] = Volatility.calculate(df)
    # values['mdd'] = RollingMDD.calculate(df)
    values['OBV'] = OBV.calculate(df)
    values['rsi'] = RSI.calculate(df)
    values['stochastic_oscillator'],_ = Stochastic_Oscillator.calculate(df)
    values['chaikin'] = Chaikin.calculate(df)
    values['accumulation_distribution'] = Accumulation_Distribution.calculate(df)
    values['money_flow_index'] = Money_Flow_Index.calculate(df)
    values['commodity_chanel_index'] = Commodity_Chanel_Index.calculate(df)
    values['ease_of_movement'] = Ease_of_Movement.calculate(df,1)
    values['coppock_curve'] = Coppock_Curve.calculate(df)
    # values['MACD'] = MACD.calculate(df)
    # values['var_90'] = VaR.calculate(df, 1).var_90.values
    values['timestamp'] = df['timestamp']
    values['timestamp'] = pd.to_datetime(values['timestamp'])
    values = values.set_index('timestamp')
    plot_grid(values)
