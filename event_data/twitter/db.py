import sqlite3

DB_NAME = "./crypto.db"
conn = sqlite3.connect(DB_NAME)

"""
conn.execute('''
    CREATE TABLE USER(
        ID CHAR(20) PRIMARY KEY NOT NULL,
        USERNAME CHAR(30) NOT NULL,
        LOCATION TEXT,
        FOLLOWER_COUNT INT,
        FOLLOWING_COUNT INT,
        TWEET_COUNT INT,
        LISTED_COUNT INT,
        VERIFIED BOOLEAN,
        PROTECTED BOOLEAN,
        IS_FOLLOWER INT
    );
''')
"""

print("created table USER")

conn.execute('''
      CREATE TABLE TWEET(
          ID TEXT PRIMARY KEY NOT NULL,
          BODY TEXT NOT NULL,
          AUTHOR_ID CHAR(20) NOT NULL,
          CREATED_AT TEXT NOT NULL,
          LIKE_COUNT INTEGER,
          REPLY_COUNT INTEGER,
          RETWEET_COUNT INTEGER,
          QUOTE_COUNT INTEGER,
          FOREIGN KEY(AUTHOR_ID) REFERENCES USER(ID)
      );  
''')

print("created table TWEET")

