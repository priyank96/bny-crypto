import pandas as pd
from util import plot
from price_data import read_price_data


class MDD:

    @staticmethod
    def calculate(df: pd.DataFrame):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].cummax()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return rolling_drawdown.cummin()


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
    values['timestamp'] = df['timestamp']
    values = values.set_index('timestamp')
    plot(values)
