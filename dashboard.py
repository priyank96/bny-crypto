import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import datetime
from datetime import timedelta

import streamlit as st  # 🎈 data web app development
import streamlit_helpers
from plots import plots
import random

from event_data import DashboardNewsData # In event_data/api.py

# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard",
                   page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

# st.balloons()
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
    starting_date = datetime.datetime(2022, 2, 21, 5, 0, 0, 0) # Dummy value
    date = st.date_input("Start Date:", starting_date)
    # end_time = st.time_input("Start Time:", streamlit_helpers.round_time(datetime.datetime.now()))
    end_time = st.time_input("Start Time:", streamlit_helpers.round_time(starting_date, mins_delta=30))
    # end_time = st.time_input("Start Time:")
    end_time = datetime.datetime.combine(date, end_time)
    if end_time > datetime.datetime.now():
        st.error("Start Time cannot be in the future!")
    start_time = end_time - pd.to_timedelta(lookback_period)

    if st.button("Refresh"):
        st.experimental_rerun()

# Main Body
highlight_color = '#e3a72f'
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
# st.markdown('----')

price_data_df = pd.read_csv("new_values.csv")

tab_overview, tab_social, tab_news, tab4 = st.tabs(["Overview 🚨", "Twitter 🐦", "News 📰", "More? 🤔"])

with tab_overview:
    # FMDD Numbers
    price_data_df_24h = price_data_df.query(f'timestamp <= "{str(end_time)}"').iloc[-25:]
    fmdd_values = [round(x,3) for x in price_data_df_24h['Forward MDD'].values]
    fmdd_delta = round(100*(fmdd_values[-1]-fmdd_values[-2])/(fmdd_values[-1]+10**-9),1)
    # Price Numbers
    price_values = [round(x,3) for x in price_data_df_24h['close'].values]
    price_delta = round(100*(price_values[-1]-price_values[-2])/(price_values[-1]+10**-9),1)
    # Volume Numbers
    volume_values = [round(x,0) for x in price_data_df_24h['volume'].values]
    volume_delta = round(100*(volume_values[-1]-volume_values[-2])/(volume_values[-1]+10**-9),1)

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Forward MDD - Risk of Price Fall", value=fmdd_values[-1], delta=f"{fmdd_delta}%", delta_color="inverse")
    col2.metric(label=f"{asset} Price", value=f'${price_values[-1]}', delta=f"{price_delta}%")
    col3.metric(label=f"{asset} Volume", value=f'{volume_values[-1]}', delta=f"{volume_delta}%")
    
    st.plotly_chart(plots.line_plot_single(price_data_df_24h, column_x = 'timestamp', column_y='Forward MDD', 
                                                   line_name="Forward MDD", line_color='red', fill='tozeroy', title='Forward MDD (24h)'),
                        use_container_width=True)

    st.plotly_chart(plots.line_plot_double_shared(price_data_df_24h, column_x = 'timestamp', column_y1='close', column_y2='volume', 
                                                   line_name1="Price", line_name2='Volume', line_color1=highlight_color, title='Price and Volume (24h) Shared'),
                        use_container_width=True)


