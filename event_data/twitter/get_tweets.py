import time
import tweepy
import sqlite3
import tqdm

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANhqjwEAAAAAFSduWwMBsRMD%2FDm3M6Fo8OLN%2Bxw%3DFFZnjLddTo9SfoYEQqzIsyhw17CDxgM9w3dSINAYMePWN0hVk1"
DB_NAME = "./crypto.db"

#  https://docs.tweepy.org/en/stable/auth_tutorial.html#auth-tutorial
api = tweepy.Client(bearer_token=BEARER_TOKEN,
                    wait_on_rate_limit=True
                    )
conn = sqlite3.connect(DB_NAME)


def get_tweets():
    cursor = conn.cursor()
    total_user_count = cursor.execute('''SELECT COUNT(*) FROM USER;''').fetchone()[0]
    cursor.execute('''SELECT ID FROM USER ORDER BY FOLLOWING_COUNT DESC;''')
    i = 0
    for user_id in tqdm.tqdm(cursor, total=total_user_count):
        if i < 10136:
            i += 1
            continue
        response = api.get_users_tweets(
            id=user_id[0],
            exclude=['retweets,replies'],
            tweet_fields=['author_id', 'created_at', 'public_metrics'],
            max_results=20,
            start_time='2020-01-01T00:00:00Z'
        )
        tweets = response.data
        next_token = response.meta.get('next_token')

        if tweets is None:
            continue

        for tweet in tweets:
            tweet_db = (tweet.id, tweet.text, tweet.author_id, str(tweet.created_at),
                        tweet.public_metrics['like_count'], tweet.public_metrics['reply_count'],
                        tweet.public_metrics['retweet_count'], tweet.public_metrics['quote_count']
                        )
            conn.execute('''
                INSERT OR REPLACE INTO TWEET(id,body,author_id,created_at,like_count,reply_count,retweet_count,quote_count)
                VALUES(?,?,?,?,?,?,?,?);
            ''', tweet_db)
            conn.commit()

        while next_token is not None:
            response = api.get_users_tweets(
                id=user_id[0],
                exclude=['retweets,replies'],
                tweet_fields=['author_id', 'created_at', 'public_metrics'],
                max_results=20,
                start_time='2020-01-01T00:00:00Z',
                pagination_token=next_token
            )
            tweets = response.data
            next_token = response.meta.get('next_token')

            if tweets is None:
                break

            for tweet in tweets:
                tweet_db = (tweet.id, tweet.text, tweet.author_id, str(tweet.created_at),
                            tweet.public_metrics['like_count'], tweet.public_metrics['reply_count'],
                            tweet.public_metrics['retweet_count'], tweet.public_metrics['quote_count']
                            )
                conn.execute('''
                            INSERT OR REPLACE INTO TWEET(id,body,author_id,created_at,like_count,reply_count,retweet_count,quote_count)
                            VALUES(?,?,?,?,?,?,?,?);
                        ''', tweet_db)
                conn.commit()

        time.sleep(1.5)


if __name__ == '__main__':
    get_tweets()
