import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import datetime

import streamlit as st  # 🎈 data web app development
import streamlit_helpers, plots.plots as plots 
import random

# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard", page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)
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
    st.image("images/crisys_logo.png", use_column_width=True)
    st.title("Dashboard")
    asset = st.selectbox("Choose Asset:", ["BTC", "ETH"])
    time_interval = st.selectbox("Time Intervals:", ["15m", "1h", "6h", "1d"])
    lookback_period = st.selectbox("Lookback Period:", ["6h", "24h"])
    date = st.date_input(
    "Start Date:",
    datetime.date(2019, 1, 16))
    if st.button("Refresh"):
        st.experimental_rerun()


# Main Body
st.title(f"Dashboard for {asset}")
st.markdown('----')

with st.container():
    st.plotly_chart(plots.prediction_horizon_bar_chart(0.2, 0.5))

st.markdown('----')
col1, col2 = st.columns(2)

with col1:
    if asset == "BTC": # Show BTC Fear and Greed Index
        st.image(f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{str(date).replace('-0', '-')}.png", use_column_width=True)

with col2:
    with st.expander(f"News Summary", expanded=True):
        st.write(f"For previous {lookback_period} of {asset}")

