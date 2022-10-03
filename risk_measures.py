import pandas as pd

from price_data import read_price_data


class MDD:
    def __init__(self):
        pass

    def calculate(self, df: pd.DataFrame):
        #  from https://quant.stackexchange.com/a/45407
        roll_max = df['close'].cummax()
        rolling_drawdown = df['close'] / roll_max - 1.0
        return rolling_drawdown.cummin()


if __name__ == '__main__':
    mdd = MDD()
    df = read_price_data('BTC', '2021-01-01', '2021-01-20', 'Daily')
    print(mdd.calculate(df))