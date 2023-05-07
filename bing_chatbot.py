import asyncio
from EdgeGPT import Chatbot, ConversationStyle
import json
import time
from sys import argv

async def ask_bing(input_prompt, Bing_API_KEY):
    bot = Chatbot(cookies=Bing_API_KEY)
    # input_prompt = input("User: ")
    wait_count = 0
    while True:
        reply_dict = await bot.ask(prompt=input_prompt, conversation_style=ConversationStyle.precise, wss_link="wss://sydney.bing.com/sydney/ChatHub")
        # print(f"User: {reply_dict['item']['messages'][0]['text']}")
        reply = reply_dict['item']['messages'][1]['text']
        if 'Searching the web for' not in reply:
            await bot.close()
            return reply

if __name__ == "__main__":
    with open('cookies.json', 'r') as f: # Download from: https://drive.google.com/drive/u/0/folders/1yaSUB0mIycoLPF11ZXiWGsM47PxfdZCH
        Bing_API_KEY = json.load(f)
    input_prompt = " ".join(argv[1:])
    print(f"Input: {input_prompt}")
    print(f"Reply: {asyncio.run(ask_bing(input_prompt, Bing_API_KEY))}")