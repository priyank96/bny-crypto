import itertools

import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import CrosshairTool, HoverTool, Span
from bokeh.palettes import Dark2_5 as palette
from bokeh.plotting import figure, show


def plot_grid(df: pd.DataFrame, event_lines: pd.DataFrame = None):
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

    if event_lines is not None:
        vlines = []
        for index, row in event_lines.iterrows():
            if row.get('sentiment', 0) == 0:
                color = 'purple'
            elif row['sentiment'] == 1:
                color = 'green'
            else:
                color = 'red'
            vlines.append(Span(location=index, dimension='height', line_color=color, line_width=1))

        for fig in figs:
            for vline in vlines:
                fig.add_layout(vline)
    show(gridplot(figs, sizing_mode='scale_both', merge_tools=True, ncols=1, width=1500, height=200))


def plot(df: pd.DataFrame, event_lines: pd.DataFrame = None):
    color = itertools.cycle(palette)
    crosshair = CrosshairTool(dimensions="both")
    hover = HoverTool(tooltips=[('Time', '$x{%F}'),
                                ('value', '$y')],
                      formatters={'$x': 'datetime'},
                      mode='mouse',
                      line_policy='nearest')
    fig = figure(x_axis_type='datetime', width=1500, height=600)
    fig.add_tools(crosshair)
    fig.add_tools(hover)

    for i, c in enumerate(df.columns):
        fig.line(x=df.index.values, y=df[c], color=next(color), legend_label=c)

    if event_lines is not None:
        vlines = []
        for index, row in event_lines.iterrows():
            if row.get('sentiment', 0) == 1:
                color = 'green'
            else:
                color = 'red'
            vlines.append(Span(location=index, dimension='height', line_color=color, line_width=1))

        for vline in vlines:
            fig.add_layout(vline)
    show(fig)
