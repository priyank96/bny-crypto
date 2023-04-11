import datetime
from datetime import timedelta
import math

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

def round_time(dt, mins_delta=30):
    delta = timedelta(minutes=mins_delta)
    return datetime.datetime.min + math.floor((dt - datetime.datetime.min) / delta) * delta