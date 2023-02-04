import plotly.graph_objects as go

def prediction_horizon_bar_chart(postitive_chance = 0.2, negative_chance = 0.5):

    neutral_chance = 1 - postitive_chance - negative_chance
    title = ''
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
            color='rgba(0, 255, 0, 1)',
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
            color='rgba(170, 170, 170, 1)',
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
            color='rgba(255, 0, 0, 1)',
            # line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
        ),
        showlegend=False
    ))

    fig.update_layout(barmode='stack', height=200, title="Price Movement")

    return fig