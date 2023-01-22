import sqlite3
import time
import tweepy

import pandas as pd

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANhqjwEAAAAAFSduWwMBsRMD%2FDm3M6Fo8OLN%2Bxw%3DFFZnjLddTo9SfoYEQqzIsyhw17CDxgM9w3dSINAYMePWN0hVk1"
DB_NAME = "./crypto.db"

#  https://docs.tweepy.org/en/stable/auth_tutorial.html#auth-tutorial
api = tweepy.Client(bearer_token=BEARER_TOKEN,
                    wait_on_rate_limit=True
                    )
conn = sqlite3.connect(DB_NAME)

if __name__ == '__main__':
    df = pd.read_sql('''
    select * from tweet
    ''', conn)
    print(df.info())
    df = (pd.to_datetime(df['CREATED_AT'])
          .dt.floor('d')
          .value_counts()
          .rename_axis('date')
          .reset_index(name='count'))
    print(df.info())
    df.to_csv('C:\\Users\\admin\\Documents\\Capstone\\bny-crypto\\event_data\\data\\tweet_counts.csv', index=False)
