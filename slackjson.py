#!/usr/bin/python2.7
#
# Send json data to Slack
# by Joel Sutton <innerteapot@gmail.com>
#
"""
This script takes the json output file of updatejson.py, sends some stats data
to Slack via a web hook, and then updates a flag in the json file.
"""

__version__ = "1.0"

import argparse
import json
import os.path
import pprint
import requests

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

    if data["slack"] != "NO":
        if args.debug:
            print "Already sent!"
        exit(0)

    if args.debug:
        print "===> Sending data to slack"

    u = "https://hooks.slack.com/services/"
    h = {
            'content-type': 'application/json',
        }
    payload = {}
    payload["text"] = "Current Track: %s\nListener Count: %s" % (
        data["current_track"], 
        data["total_listeners"]) 
    r = requests.post(u, headers=h, json=payload, timeout=5)

    if args.debug:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(r.text)

    if r.text != "ok":
        exit(1)

    data["slack"] = "YES"

    with open(args.file, 'w') as outfile:
        json.dump(data, outfile)

    if args.debug:
        print "===> Payload data"
        pp.pprint(payload)
        print "===> json data"
        pp.pprint(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send data to Slack and update json file')
    parser.add_argument("file", help="json file")
    parser.add_argument("--debug", help="enable debugging output", \
                        action="store_true")
    args = parser.parse_args()

    main(args)

