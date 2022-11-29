import sqlite3

DB_NAME = "./crypto.db"
conn = sqlite3.connect(DB_NAME)

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

print("created table USER")
