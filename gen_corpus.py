#! /usr/bin/env python

from pymongo import MongoClient
import config
import re
import sys

client = MongoClient('mongodb://localhost')

TWEETS = None
USERS = None

def main(argv):
    # Set DBs
    if config.DEVELOPER_MODE:
        authenticated = client.dev_tweets.authenticate(
            config.DEV_DB_USER, config.DEV_DB_PASSWORD)
        db = client.dev_tweets
    else:
        authenticated = client.tweets.authenticate(config.DB_USER, config.DB_PASSWORD)
        db = client.tweets

    # Set Collections
    global TWEETS
    TWEETS = db.tweets
    global USERS
    USERS = db.users
    
    for tweet in TWEETS.find({"is_quote_status": False}):
        t = re.sub(r"\n", " ", tweet['text'])
        print t.encode('utf8')

if __name__ == "__main__":
    main(sys.argv[1:])
