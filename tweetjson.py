#!/usr/bin/python2.7
#
# Tweet json data
# by Joel Sutton <innerteapot@gmail.com>
#
"""
This script takes the json output file of updatejson.py, tweets the currently
playing track, and then updates a flag in the json file.
"""

__version__ = "1.0"

import argparse
import json
import os.path
import pprint
import requests
import tweepy


def main(args):
    # mute warnings to make cron triggering smoother on Ubuntu 14.04 LTS
    requests.packages.urllib3.disable_warnings()

    if os.path.isfile(args.file):
        with open(args.file) as json_file:
            data = json.load(json_file)
    else:
        if args.debug:
            print "Unable to find file!"
        exit(1)

    if data["tweeted"] != "NO":
        if args.debug:
            print "Already tweeted!"
        exit(0)

    # Consumer keys and access tokens, used for OAuth
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''
     
    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
     
    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)
        
    if args.debug:
        print "===> Sending data to twitter"
    
    try:
        api.update_status("#NowPlaying %s #ambient http://radio.com" % 
            data["current_track"])
    except tweepy.TweepError:
        if args.debug:
            print "Duplicate tweet! Marking as sent."

    data["tweeted"] = "YES"

    with open(args.file, 'w') as outfile:
        json.dump(data, outfile)

    if args.debug:
        pp = pprint.PrettyPrinter(indent=4)
        print "===> json data saved"
        pp.pprint(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tweet data and update json file')
    parser.add_argument("file", help="json file")
    parser.add_argument("--debug", help="enable debugging output", \
                        action="store_true")
    args = parser.parse_args()

    main(args)

