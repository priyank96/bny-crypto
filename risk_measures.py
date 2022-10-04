import numpy as np
import pandas as pd
from scipy.stats import norm

from price_data import read_price_data
from util import plot_grid


class MDD:
    """
    Maximum Drawdown
    Definition: A maximum drawdown (MDD) is the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained
    Formula: MDD = (Trough Value - Peak Value)/Peak Value
    """

    @staticmethod
    def calculate(df: pd.DataFrame):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].cummax()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return -1*rolling_drawdown.cummin()


class VaR:
    """
    Value at Risk
    Definition: Value at risk (VaR) is a statistic that quantifies the extent of possible financial losses

    Calculation:
                Method 1 Hist Simulation: Sort daily returns and return corresponding percentiles
                Method 2 Variance Covariance: find mean and std dev of returns and return corresponding confidence level of VaR
    """

    @staticmethod
    def calculate_var_row(df: pd.DataFrame, method: int):
        # from https://blog.quantinsti.com/calculating-value-at-risk-in-excel-python/
        df_temp = pd.DataFrame()
        df_temp["pct"] = df["close"].pct_change()
        if method == 1:
            sorted_returns = df_temp.sort_values("pct")['pct']
            var90 = sorted_returns.quantile(0.1)
            var95 = sorted_returns.quantile(0.05)
            var99 = sorted_returns.quantile(0.01)
            return {"var_90": [-1*var90],
                    "var_95": [-1*var95],
                    "var_99": [-1*var99]}
        else:
            mean = np.mean(df_temp.pct)
            std = np.std(df_temp.pct)
            var90 = norm.ppf(0.1, mean, std)
            var95 = norm.ppf(0.05, mean, std)
            var99 = norm.ppf(0.01, mean, std)
            return {"var_90": [-1*var90],
                    "var_95": [-1*var95],
                    "var_99": [-1*var99]}

    @staticmethod
    def calculate(df: pd.DataFrame, method: int):
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


if __name__ == '__main__':
    df = read_price_data('BTC', '2021-01-01', '2021-10-20', 'Daily')
    values = pd.DataFrame()
    values['close'] = df['close']
    values['volatility'] = Volatility.calculate(df)
    values['mdd'] = MDD.calculate(df)
    values['var_90'] = VaR.calculate(df, 1).var_90.values
    values['timestamp'] = df['timestamp']
    values = values.set_index('timestamp')
    plot_grid(values)
