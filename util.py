import pandas as pd
import pandas_bokeh


def plot(df: pd.DataFrame):
    df.plot_bokeh(figsize=(1500, 750))
