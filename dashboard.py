import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import streamlit_helpers

# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard", page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.markdown(streamlit_helpers.hide_streamlit_style, unsafe_allow_html=True) 

with st.sidebar:
    st.image("images/crisys_logo.png", use_column_width=True)
    st.title("Dashboard")
    st.selectbox("Choose Asset:", ["BTC", "ETH"])
    st.selectbox("Timeperiod:", ["15m", "1h", "6h", "1d"])



st.title("Real-Time / Live Data Science Dashboard")

