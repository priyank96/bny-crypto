import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import datetime
from datetime import timedelta

import streamlit as st  # 🎈 data web app development
import streamlit_helpers, plots.plots as plots
import random

from event_data import DashboardNewsData # In event_data/api.py

# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard",
                   page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.markdown(streamlit_helpers.hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #ff5555;
        color:#ffffff;
    }
    div.stButton > button:hover {
        background-color: #e3a72f;
        color:#ffffff;
        }
    </style>""", unsafe_allow_html=True)

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

with st.sidebar:
    st.image("images/crisys_logo.png", width=200)
    st.title("Dashboard")
    asset = st.selectbox("Choose Asset:", ["BTC", "ETH"])
    time_interval = st.selectbox("Time Intervals:", ["30Min", "1h", "6h", "1d"])
    lookback_period = st.selectbox("Lookback Period:", ["6h", "24h"])
    starting_date = datetime.datetime(2019, 2, 21, 5, 0, 0, 0) # Dummy value
    date = st.date_input("Start Date:", starting_date)
    # end_time = st.time_input("Start Time:", streamlit_helpers.round_time(datetime.datetime.now()))
    end_time = st.time_input("Start Time:", streamlit_helpers.round_time(starting_date))
    # end_time = st.time_input("Start Time:")
    end_time = datetime.datetime.combine(date, end_time)
    if end_time > datetime.datetime.now():
        st.error("Start Time cannot be in the future!")
    start_time = end_time - pd.to_timedelta(lookback_period)

    if st.button("Refresh"):
        st.experimental_rerun()

# Main Body
st.markdown(f"""
<style>
    div.block-container{{
        padding-top: 0;
    }}
    .highlight{{
        color: #e3a72f;
    }}
</style>
<h3>Dashboard for <span class='highlight'>{asset}</span> 
in <span class='highlight'>{time_interval}</span> 
intervals and <span class='highlight'>{lookback_period}</span> lookback period
at <span class='highlight'>{end_time.strftime("%Y-%m-%d %H:%M")}</span></h3>
""", unsafe_allow_html=True)
# st.title(f"Dashboard for {asset} in {time_interval} intervals and {lookback_period} lookback period")
st.markdown('----')

with st.container():
    # Dummy values
    st.markdown(f"""
<style>
    div.block-container{{
        padding-top: 0;
    }}
    .highlight{{
        color: #e3a72f;
    }}
</style>
<h4>Risk Score</h4>
""", unsafe_allow_html=True)
    increase_risk = 20
    delta_increase_risk = 7
    decrease_risk = 50
    delta_decrease_risk = -2
    col1, col2, col3 = st.columns(3)
    col1.metric("CRYSys Score", f"{decrease_risk-increase_risk}%", f"{delta_decrease_risk-delta_increase_risk}%")
    col2.metric("Risk to Increase", f"{increase_risk}%", f"{delta_increase_risk}%")
    col3.metric("Risk to Decrease", f"{decrease_risk}%", f"{delta_decrease_risk}%")

    st.plotly_chart(plots.prediction_horizon_bar_plot(increase_risk/100, decrease_risk/100), use_container_width=True)


st.markdown('----')
col1, col2, col3 = st.columns(3)

with col1:
    
    # with st.expander(f"Sentiment Trend", expanded=False):
    #     st.plotly_chart(plots.sentiment_line_plot(title='Sentiment', n=10), use_container_width=True)

    with st.expander(f"News Sentiment Trend", expanded=True):
        df = DashboardNewsData.dashboard_news_aggregated_sentiment(asset, start_time, end_time)
        st.plotly_chart(plots.news_sentiment_line_plot(df, title='Sentiment'),
                        use_container_width=True)

    with st.expander(f"Mentions", expanded=True):
        st.plotly_chart(plots.mentions_line_plot(title='Mentions', n=10), use_container_width=True)

    if asset == "BTC":  # Show BTC Fear and Greed Index
        with st.expander(f"Fear & Greed Index", expanded=True):
            st.image(
                f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{str(date).replace('-0', '-')}.png",
                use_column_width=True)

with col2:
    with st.expander(f"News Summary", expanded=True):
        article_df = DashboardNewsData.dashboard_news_articles_to_show(asset, start_time, end_time)
        if len(article_df) == 0:
            st.write(" ")
        for i in range(len(article_df)):
            st.markdown(f"""
                <h5>{article_df.iloc[i]['title']}</h5>
                <strong>{article_df.iloc[i]['subheadlines']}</strong><br/>
                Sentiment: {article_df.iloc[i]['sentiment_logits']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Topic: {article_df.iloc[i]['class_labels']}
            """ + (i < (len(article_df)-1))*'<hr/>', unsafe_allow_html=True)
with col3:
    with st.expander(f"Top Mentions", expanded=True):
        st.write(f"TODO: Put tweets + news")
