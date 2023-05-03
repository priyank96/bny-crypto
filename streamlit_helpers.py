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
url = "https://chatgpt-4-bing-ai-chat-api.p.rapidapi.com/chatgpt-4-bing-ai-chat-api/0.2/send-message/"

payload = {
	"bing_u_cookie": "1ehrO3MbFrM37PH57fboByHcyaZi_BCt-tqr38idYUw1oDJXw3v99Vf82MWSS8W4AGU_BaFdBRNShBIy7_o8rBKNEIDYQm_uVxogSsvOWjK7fB12lHgQQWIP5PD0sOBkI49Yd7PSGfXBUTd59Uepxs2UUdmeoAIsRMlSGBYYFSTP6XYa8mz2XQEpvQ_rD8RXbo2uNv0hXMEsvGweujGikyA",
	"question": "Give me 3 examples of how I can use you."
}
headers = {
	"content-type": "application/x-www-form-urlencoded",
	"X-RapidAPI-Key": "3544cf43d4msh1ed76e82c2c2d91p11cb52jsnc07ced28aeca",
	"X-RapidAPI-Host": "chatgpt-4-bing-ai-chat-api.p.rapidapi.com"
}

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
