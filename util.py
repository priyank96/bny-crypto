import itertools

import pandas as pd
import pandas_bokeh
from bokeh.palettes import Dark2_5 as palette
from bokeh.models import CrosshairTool


def plot_grid(df: pd.DataFrame):
    figs = []
    color = itertools.cycle(palette)
    crosshair = CrosshairTool(dimensions="both")
    for c in df.columns:
        fig = df[c].plot_bokeh(show_figure=False, color=next(color))
        fig.add_tools(crosshair)
        fig.xaxis.visible = False
        figs.append(fig)
    pandas_bokeh.plot_grid(figs, sizing_mode='scale_both', merge_tools=True, ncols=1, width=1500, height=150)


def plot(df: pd.DataFrame):
    df.plot_bokeh(figsize=(1500, 750))
