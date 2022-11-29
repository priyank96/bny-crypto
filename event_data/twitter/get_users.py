import sqlite3
import time

import tweepy

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANhqjwEAAAAAFSduWwMBsRMD%2FDm3M6Fo8OLN%2Bxw%3DFFZnjLddTo9SfoYEQqzIsyhw17CDxgM9w3dSINAYMePWN0hVk1"
DB_NAME = "./crypto.db"

#  https://docs.tweepy.org/en/stable/auth_tutorial.html#auth-tutorial
api = tweepy.Client(bearer_token=BEARER_TOKEN,
                    wait_on_rate_limit=True
                    )
conn = sqlite3.connect(DB_NAME)


def __add_user(user, is_follower):
    user_db = (user.id, user.username, user.location,
               user.public_metrics['followers_count'], user.public_metrics['following_count'],
               user.public_metrics['tweet_count'], user.public_metrics['listed_count'],
               user.verified, user.protected, is_follower)
    conn.execute('''
        INSERT OR REPLACE INTO user(id,username,location,follower_count,following_count,tweet_count,listed_count,verified,protected,IS_FOLLOWER)
        values(?,?,?,?,?,?,?,?,?,?);
        ''', user_db)


def get_usernames_following(ids):
    """ can only do lookup in steps of 100;
        so 'ids' should be a list of 100 ids
    """
    user_objs = api.get_users(usernames=ids, user_fields=["public_metrics", "location", "verified", "protected"]).data
    for user in user_objs:
        print("following: " + str(user.id) + " " + str(user.username))
        # add the user
        __add_user(user, 0)
        # add the user's following
        follower_users = api.get_users_following(
            id=user.id,
            user_fields=["public_metrics", "location", "verified", "protected"],
            max_results=1000
        )
        next_token = follower_users.meta.get('next_token')
        for follower in follower_users.data:
            __add_user(follower, 0)
        conn.commit()
        time.sleep(60)

        while next_token is not None:
            follower_users = api.get_users_following(
                id=user.id,
                user_fields=["public_metrics", "location", "verified", "protected"],
                max_results=1000,
                pagination_token=next_token
            )
            next_token = follower_users.meta.get('next_token')
            for follower in follower_users.data:
                __add_user(follower, 0)
            conn.commit()
            time.sleep(60)
        conn.commit()


def get_usernames_followers(ids):
    """ can only do lookup in steps of 100;
        so 'ids' should be a list of 100 ids
    """
    user_objs = api.get_users(usernames=ids).data
    for user in user_objs:
        print("follower: " + str(user.id) + " " + str(user.username))
        # add the user's followers
        follower_count = 0
        follower_users = api.get_users_followers(
            id=user.id,
            user_fields=["public_metrics", "location", "verified", "protected"],
            max_results=1000
        )
        next_token = follower_users.meta.get('next_token')
        for follower in follower_users.data:
            __add_user(follower, 1)
            follower_count += 1
        conn.commit()
        time.sleep(60)

        while next_token is not None:
            follower_users = api.get_users_followers(
                id=user.id,
                user_fields=["public_metrics", "location", "verified", "protected"],
                max_results=1000,
                pagination_token=next_token
            )
            next_token = follower_users.meta.get('next_token')
            for follower in follower_users.data:
                __add_user(follower, 1)
                follower_count += 1
                if follower_count >= 1000:
                    break

            conn.commit()
            time.sleep(60)
            if follower_count >= 1000:
                break

        conn.commit()
        if follower_count >= 1000:
            continue


if __name__ == '__main__':
    users = ['Bybit_Official', 'APompliano', 'ErikVoorhees', 'VitalikButerin', 'IvanOnTech', 'MessariCrypto',
             'TheCryptoDog', 'mdudas', 'PaikCapital', 'SushiSwap', 'saylor', 'girlgone_crypto', '100trillionUSD',
             'KennethBosak', 'CryptoKaleo', 'WClementeIII', 'BTC_Archive', 'LynAldenContact', 'CryptoDiffer',
             'TheMoonCarl', 'CryptoWendyO', 'nic__carter', 'whale_alert', 'AltcoinGordon', 'lopp', 'cz_binance',
             'ASvanevik', 'opensea', 'TyDanielSmith', 'masonnystrom', 'ToneVays', 'ethereumJoseph']
    get_usernames_following(users)
    # get_usernames_followers(users)

