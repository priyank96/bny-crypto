import datetime
from datetime import timedelta
import math
import requests

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
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

if __name__ == "__main__":
    print(f"Requesting: {payload['question']}")
    response = requests.post(url, data=payload, headers=headers)

    print(response.json())