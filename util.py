import itertools

import pandas as pd
import pandas_bokeh
from bokeh.plotting import figure, show
from bokeh.palettes import Dark2_5 as palette
from bokeh.models import CrosshairTool, HoverTool, Span
from bokeh.layouts import gridplot


def plot_grid(df: pd.DataFrame, vertical_lines: pd.DataFrame):
    figs = []
    color = itertools.cycle(palette)
    crosshair = CrosshairTool(dimensions="both")
    hover = HoverTool(tooltips=[('Time', '$x{%F}'),
                                ('value', '$y')],
                      formatters={'$x': 'datetime'},
                      mode='mouse',
                      line_policy='nearest')
    first_fig = None
    for i, c in enumerate(df.columns):
        if i == 0:
            fig = figure(x_axis_type='datetime')
            fig.line(x=df.index.values, y=df[c], color=next(color), legend_label=c)
            first_fig = fig
        else:
            fig = figure(x_range=first_fig.x_range, x_axis_type='datetime')
            fig.line(x=df.index.values, y=df[c], color=next(color), legend_label=c)

        fig.add_tools(crosshair)
        fig.add_tools(hover)
        fig.xaxis.visible = False
        figs.append(fig)

    vlines = []
    for index, row in vertical_lines.iterrows():
        if row['sentiment'] == 1:
            color = 'green'
        else:
            color = 'red'
        vlines.append(Span(location=index, dimension='height', line_color=color, line_width=1))

    for fig in figs:
        for vline in vlines:
            fig.add_layout(vline)
    show(gridplot(figs, sizing_mode='scale_both', merge_tools=True, ncols=1, width=1500, height=200))


def plot(df: pd.DataFrame):
    df.plot_bokeh(figsize=(1500, 750))
