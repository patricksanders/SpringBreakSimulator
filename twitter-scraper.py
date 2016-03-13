#! /usr/bin/env python
#######################################################################
# Author: Patrick Sanders
# Adapted from: https://github.com/starrynightstudios/twitter-scraper
# License: MIT
#######################################################################
from twython import TwythonStreamer, Twython
from pymongo import MongoClient
import datetime
import threading
import logging
import sys
import getopt
import config

# ==================================================
# WHAT TO TRACK, HASHTAGS, MENTIONS, ETC.
# ==================================================
#
# Set what to watch for
TRACK_BY = ['#springbreak', '#springbreak2k16', '#sb2k16', '#pcb2k16']

# Set up Mongodb
client = MongoClient('mongodb://localhost')
# Set Collections, these get set in main
TWEETS = None
USERS = None

class TwitterStreamer(TwythonStreamer):
    """
    TwitterStreamer is going to be our Twitter watch.  It streams all data happening on Twitter for the terms
    that we have told it to search for.  It will then save all of those tweets to a Mongodb for our use
    and pleasure.
    """

    def on_success(self, tweet):
        if 'text' in tweet:
            # Get Coordinates
            has_coords = False
            if tweet['coordinates'] or tweet['place']:
                has_coords = True
                coords_message = 'Tweet has coordinates!'
                logging.info(coords_message)
                if VERBOSE:
                    print coords_message
            # Save Tweet
            TWEETS.insert(tweet)
            # Save Mentions
            self.save_mentions(tweet)

    def on_error(self, status_code, data):
        # This method tells us there was an error
        logging.error(status_code)
        print status_code

    def save_mentions(self, tweet):
        for mention in tweet['entities']['user_mentions']:
            screen_name = USERS.find_one({'twitter': mention['screen_name']})
            # If no user (mention) was found in our database let's save it
            if not screen_name:
                USERS.insert({
                    'twitter': mention['screen_name'],
                    'created': datetime.datetime.utcnow(),
                    'mentioned_by': tweet['user']['screen_name']
                })
                added_message = 'Added @%s! %s' % (
                    mention['screen_name'], datetime.datetime.now())
                logging.info(added_message)
                if VERBOSE:
                    print added_message


def run_stream():
    stream = TwitterStreamer(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    started_message = 'Started Twitter Scraper!!! %s' % datetime.datetime.now()
    logging.info(started_message)
    if VERBOSE:
        print started_message

    if DEVELOPER_MODE:
        # Get Worldwide trending topics to filter by for development
        twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET,
                          ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        trending = twitter.get_place_trends(id=1)[0]['trends']
        global TRACK_BY
        TRACK_BY = []
        for trend in trending:
            TRACK_BY.append(trend['name'])
    if VERBOSE:
        print 'Scraping tweets with any of the following: %s' % TRACK_BY
    stream.statuses.filter(track=TRACK_BY)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hd:v:")
    except getopt.GetoptError:
        print 'twitter-scraper.py -d <development_mode> -v <verbose>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'twitter-scraper.py -d <development_mode> -v <verbose>'
            sys.exit()
        elif opt in ("-d"):
            if arg == 'true':
                global DEVELOPER_MODE
                DEVELOPER_MODE = True
                print 'Developer Mode ENGAGED!'
        elif opt in ("-v"):
            if arg == 'true':
                global VERBOSE
                VERBOSE = True
                print 'PRINT ALL THE THINGS!!!'

    # Start Logging
    logging.basicConfig(filename='twitter-scraper.log', level=logging.DEBUG)

    # Set DBs
    if DEVELOPER_MODE:
        authenticated = client.dev_tweets.authenticate(
            DEV_DB_USER, DEV_DB_PASSWORD)
        db = client.dev_tweets
    else:
        authenticated = client.tweets.authenticate(DB_USER, DB_PASSWORD)
        db = client.tweets

    # Set Collections
    global TWEETS
    TWEETS = db.tweets
    global USERS
    USERS = db.users

    # BEGIN THE STREAM!!!
    run_stream()

if __name__ == "__main__":
    main(sys.argv[1:])
