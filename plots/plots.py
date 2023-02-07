import plotly.graph_objects as go
import random


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


def sentiment_line_plot(title='Trend Line Plot', n=10):
    n = 10
    x = list(range(1, n + 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[random.uniform(-1, 1) for i in range(n)], fill='tozeroy', name="Historic",
                             marker=dict(color="gray")))  # fill down to xaxis
    fig.add_trace(go.Scatter(x=x, y=[random.uniform(-1, 1) for i in range(n)], fill='tozeroy', name="Latest",
                             marker=dict(color="#e3a72f")))  # fill to trace0 y
    # fig.update_layout(title=title)

    return fig


def news_sentiment_line_plot(df, title='Trend Line Plot'):
    fig = go.Figure()
    fig.add_trace(
        go.Line(x=df.index, y=df['sentiment'], fill='tozeroy', name="Sentiment")
    )
    fig['data'][0]['showlegend'] = True
    return fig
