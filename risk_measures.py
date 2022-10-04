import string
import pandas as pd
import numpy as np
from scipy.stats import norm
from tabulate import tabulate

from price_data import read_price_data


class MDD:
    '''
    Maximum Drawdown
    Definition: A maximum drawdown (MDD) is the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained
    Formula: MDD = (Trough Value - Peak Value)/Peak Value
    '''
    def __init__(self):
        pass

    def calculate(self, df: pd.DataFrame):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].cummax()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return rolling_drawdown.cummin()

class VaR:
    '''
    Value at Risk
    Defintion: Value at risk (VaR) is a statistic that quantifies the extent of possible financial losses

    Calculation: 
                Method 1 Hist Simulation: Sort daily returns and return corresponding percentiles
                Method 2 Variance Covariance: find mean and std dev of returns and return corresponding confidence level of VaR
    '''
    def __init__(self) -> None:
        pass
    def calculate(self, df: pd.DataFrame, method: int):
        # from https://blog.quantinsti.com/calculating-value-at-risk-in-excel-python/
        df["pct"] = df["close"].pct_change()
        if method == 1:
            sorted_returns = df.sort_values("pct")['pct']
            var90 = sorted_returns.quantile(0.1)
            var95 = sorted_returns.quantile(0.05)
            var99 = sorted_returns.quantile(0.01)
            return {"var_90": var90,
                    "var_95": var95,
                    "var_99": var99}
        else:
            mean = np.mean(df.pct)
            std = np.std(df.pct)
            var90 = norm.ppf(0.1, mean, std)
            var95 = norm.ppf(0.05, mean, std)
            var90 = norm.ppf(0.01, mean, std)
            return {"var_90": var90,
                    "var_95": var95,
                    "var_99": var99}



if __name__ == '__main__':
    mdd = MDD()
    var = VaR()
    df = read_price_data('BTC', '2021-01-01', '2021-01-20', 'Daily')
    print(mdd.calculate(df))
    print(var.calculate(df, 1))
