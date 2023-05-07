import datetime
from datetime import timedelta
import math
import requests
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

def round_time(dt, mins_delta=30):
    delta = timedelta(minutes=mins_delta)
    return datetime.datetime.min + math.floor((dt - datetime.datetime.min) / delta) * delta


# Using RapidAPI to get a response from the chatbot
# https://rapidapi.com/stefano-pochet-stefano-pochet-default/api/chatgpt-4-bing-ai-chat-api

class Tweet(object):
    def __init__(self, s, embed_str=False):
        if not embed_str:
            # Use Twitter's oEmbed API
            # https://dev.twitter.com/web/embedded-tweets
            api = "https://publish.twitter.com/oembed?url={}&hide_media=true&hide_thread=true&align=center&dnt=true".format(s)
            response = requests.get(api)
            # modify utc_offset
            soup = BeautifulSoup(response.json()["html"], "html.parser")
            utc_offset = datetime.datetime.now() - datetime.datetime.utcnow()
            self.text = response.json()["html"]
        else:
            self.text = s

    def _repr_html_(self):
        return self.text

    def component(self, height=600, scrolling=True):
        return components.html(self.text, height=height, scrolling=scrolling)

if __name__ == "__main__":
    print(f"Requesting: {payload['question']}")
    response = requests.post(url, data=payload, headers=headers)

    print(response.json())
