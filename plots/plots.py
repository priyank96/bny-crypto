import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from wordcloud import WordCloud
import re
import ast
import numpy as np
import plotly.express as px


def prediction_horizon_bar_plot(postitive_chance=0.2, negative_chance=0.5, title='Risk Prediction'):
    neutral_chance = 1 - postitive_chance - negative_chance
    layout = go.Layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(layout=layout)
    fig.add_trace(go.Bar(
        y=[title],
        x=[postitive_chance],
        name='Positive',
        orientation='h',
        marker=dict(
            color='rgba(0, 255, 0, 0.7)',
            # line=dict(color='rgba(55, 255, 55, 1.0)', width=3)
        ),
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=[title],
        x=[neutral_chance],
        name='Neutral',
        orientation='h',
        marker=dict(
            color='rgba(170, 170, 170, 0.7)',
            # line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
        ),
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=[title],
        x=[negative_chance],
        name='Negative',
        orientation='h',
        marker=dict(
            color='rgba(255, 0, 0, 0.7)',
            # line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
        ),
        showlegend=False
    ))

    fig.update_layout(barmode='stack', height=200)#, title=title)

    return fig


def mentions_line_plot(title='Trend Line Plot', n=10):
    n = 10
    x = list(range(1, n + 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[random.randint(1, 10) for i in range(n)], fill='tozeroy', name="Historic",
                             marker=dict(color="gray")))  # fill down to xaxis
    fig.add_trace(go.Scatter(x=x, y=[random.randint(1, 10) for i in range(n)], fill='tozeroy', name="Latest",
                             marker=dict(color="#e3a72f")))  # fill to trace0 y
    # fig.update_layout(title=title)

    return fig


def sentiment_line_plot(title=None, n=10):
    n = 10
    x = list(range(1, n + 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[random.uniform(-1, 1) for i in range(n)], fill='tozeroy', name="Historic",
                             marker=dict(color="gray")))  # fill down to xaxis
    fig.add_trace(go.Scatter(x=x, y=[random.uniform(-1, 1) for i in range(n)], fill='tozeroy', name="Latest",
                             marker=dict(color="#e3a72f")))  # fill to trace0 y
    if title is not None:
        fig.update_layout(title_text=title)

    return fig


def line_plot_single(df, column_x=None, column_y=None, line_name=None, line_color=None, fill=None, title=None, 
                     add_hline=False, hline_value=0.03, hline_color='red', hline_annotation_text='', hline_annotation_position='top right'):
    fig = go.Figure()
    if column_x is None:
        x = df.index
    else:
        x = df[column_x]
    fig.add_trace(go.Line(x=x, y=df[column_y], fill=fill, name=line_name, marker=dict(color=line_color)))
    if add_hline:
        fig.add_hline(y=hline_value, line_width=1, line_dash="longdash", line_color=hline_color, # dash styles: ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
            annotation_text=hline_annotation_text, 
            annotation_position=hline_annotation_position,
            annotation_font_color=hline_color) 
    if title is not None:
        fig.update_layout(title_text=title)
        layout_margin_top=30
    else:
        layout_margin_top=10
    fig.update_layout(margin=dict(l=10, r=10, t=layout_margin_top, b=10), height=300, legend=dict(
        x=0,
        y=1.2), legend_orientation="h")
    fig['data'][0]['showlegend'] = True
    return fig

def line_plot_double_stacked(df, column_x=None, column_y1=None, column_y2=None, line_name1=None, line_name2=None, line_color1=None, line_color2=None, fill=None, title=None):
    # fig = go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    if column_x is None:
        x = df.index
    else:
        x = df[column_x]
    fig.append_trace(go.Line(x=x, y=df[column_y1], fill=fill, name=line_name1, marker=dict(color=line_color1)), row=1, col=1)
    fig.append_trace(go.Line(x=x, y=df[column_y2], fill=fill, name=line_name2, marker=dict(color=line_color2)), row=2, col=1)
    if title is not None:
        fig.update_layout(title_text=title)
        layout_margin_top=30
    else:
        layout_margin_top=10
    fig.update_layout(margin=dict(l=10, r=10, t=layout_margin_top, b=10), height=300, legend=dict(
        x=0,
        y=1.2), legend_orientation="h")
    
    fig['data'][0]['showlegend'] = True
    return fig

def line_plot_double_shared(df, column_x=None, column_y1=None, column_y2=None, line_name1=None, line_name2=None, line_color1=None, line_color2=None, line_fill1=None, line_fill2=None, title=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    if column_x is None:
        x = df.index
    else:
        x = df[column_x]
    fig.add_trace(go.Line(x=x, y=df[column_y1], fill=line_fill1, name=line_name1, marker=dict(color=line_color1)), secondary_y=False)
    fig.add_trace(go.Line(x=x, y=df[column_y2], name=line_name2, marker=dict(color=line_color2, opacity=0.4)), secondary_y=True)
    if title is not None:
        fig.update_layout(title_text=title)
        layout_margin_top=30
    else:
        layout_margin_top=10
    fig.update_layout(margin=dict(l=10, r=10, t=layout_margin_top, b=10), height=300, legend=dict(
        x=0,
        y=1.2), legend_orientation="h")
    # fig.update_layout(yaxis2 = dict(range=[0, 8000]))
    fig['data'][0]['showlegend'] = True
    return fig

def line_plot_double_shared_bars(df, column_x=None, column_y1=None, column_y2=None, line_name1=None, line_name2=None, line_color1=None, line_color2=None, line_fill1=None, line_fill2=None, title=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    if column_x is None:
        x = df.index
    else:
        x = df[column_x]
    fig.add_trace(go.Line(x=x, y=df[column_y1], fill=line_fill1, name=line_name1, marker=dict(color=line_color1)), secondary_y=False)
    fig.add_trace(go.Bar(x=x, y=df[column_y2], name=line_name2, marker=dict(color=line_color2, opacity=0.4)), secondary_y=True)
    if title is not None:
        fig.update_layout(title_text=title)
        layout_margin_top=30
    else:
        layout_margin_top=10
    fig.update_layout(margin=dict(l=10, r=10, t=layout_margin_top, b=10), height=300)
    fig.update_layout(yaxis2 = dict(range=[0, df[column_y2].max()]), legend=dict(
        x=0,
        y=1.2), legend_orientation="h")
    fig['data'][0]['showlegend'] = True
    return fig

def line_plot_double_shared_stacked_bars(df, column_x=None, column_y1=None, column_y2=None, line_name1=None, line_name2=None, line_color1=None, line_color2=None, line_fill1=None, line_fill2=None, title=None,
                                         add_hline=False, hline_value=0.03, hline_color='red', hline_annotation_text='', hline_annotation_position='top left'):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    if column_x is None:
        x = df.index
    else:
        x = df[column_x]

    fig.add_trace(go.Line(x=x, y=df[column_y1], fill=line_fill1, name=line_name1, marker=dict(color=line_color1)), secondary_y=False)
    if add_hline:
        fig.add_trace(go.Line(x=x, y=[hline_value]*len(x), name=hline_annotation_text, marker=dict(color=hline_color), line_dash="dash"), secondary_y=False)
    for i, (col_name, line_name, line_color)  in enumerate(zip(column_y2, line_name2, line_color2)):
        fig.add_trace(go.Bar(x=x, y=df[col_name], name=line_name, marker=dict(color=line_color, opacity=0.4)), secondary_y=True)

    # if add_hline:
    #     fig.add_hline(y=hline_value, line_width=1, line_dash="longdash", line_color=hline_color, # dash styles: ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    #         annotation_text=hline_annotation_text, 
    #         annotation_position=hline_annotation_position,
    #         annotation_font_color=hline_color)
        
    if title is not None:
        fig.update_layout(title_text=title)
        layout_margin_top=30
    else:
        layout_margin_top=10
    fig.update_layout(barmode='relative', margin=dict(l=10, r=10, t=layout_margin_top, b=10), height=300)
    fig.update_layout(yaxis2 = dict(range=[0, df[column_y2].abs().max()]), legend=dict(
        x=0,
        # y=1+(0.2*len(column_y2)),))
        y=1.2), legend_orientation="h")
    fig['data'][0]['showlegend'] = True
    return fig

def hashtag_word_cloud(hashtags):
    text = ast.literal_eval(hashtags)
    text = ' '.join(text)
    return word_cloud_gen(text)

def body_word_cloud(body):
  clean_text = re.sub(r'[^\x00-\x7F]+', '', body)
  return word_cloud_gen(clean_text)

def word_cloud_gen(text):
  # Generate a word cloud image
  wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
  image = np.array(wordcloud.to_image())

  # Create a Plotly chart to display the word cloud image
  fig = go.Figure(go.Image(z=image))
  fig.update_layout(width=800, height=400, margin=dict(l=0, r=0, t=0, b=0))
  fig.update_layout(xaxis_visible=False, yaxis_visible=False)
  return fig

def scatter_plot(df):
    fig = px.scatter(df, x='embed_PCA_1', y='embed_PCA_2', opacity = 0.1)

    fig.add_trace(go.Scatter(x=[df.iloc[-1]["embed_PCA_1"]], y=[df.iloc[-1]["embed_PCA_2"]], opacity = 1,mode='markers', marker=dict(size=20, color='black')))
    # Add shapes
    fig.add_shape(type="circle",
        xref="x", yref="y",
        x0=2.5, y0=-0.5,
        x1=3.5, y1=1,
        opacity=0.2,
        fillcolor="red",
        line_color="red",
    )
    return fig