import datetime
from datetime import timedelta
import math
import requests
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import tiktoken

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

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

if __name__ == "__main__":
    print(f"Requesting: {payload['question']}")
    response = requests.post(url, data=payload, headers=headers)

    print(response.json())
