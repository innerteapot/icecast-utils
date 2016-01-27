#!/usr/bin/python2.7
#
# Send json data to Tunein
# by Joel Sutton <innerteapot@gmail.com>
#
"""
This script takes the json output file of updatejson.py, sends some stats data
to Tunein via a get request, and then updates a flag in the json file.
"""

__version__ = "1.0"

import argparse
import json
import os.path
import pprint
import requests
from urllib import urlencode

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

    if data["tunein"] != "NO":
        if args.debug:
            print "Already sent!"
        exit(0)

    if args.debug:
        print "===> Sending data to tunein"

    # set up for urlencoding of track data ONLY
    #
    p = {}
    if " - " in data["current_track"]:
        (p["artist"], p["title"]) = data["current_track"].split(" - ")
    else:
        p["artist"] = "Unknown"
        p["title"]  = data["current_track"] 

    u =  "http://air.radiotime.com/Playing.ashx?"
    u += "partnerId=1234&partnerKey=1234&id=1234&"
    u += urlencode(p)

    r = requests.get(u, timeout=5)

    if args.debug:
        pp = pprint.PrettyPrinter(indent=4)
        print u
        pp.pprint(r.text)
        pp.pprint(r)

    #if "<status>200</status>" not in r.text:
    if r.status_code != requests.codes.ok:
        exit(1)

    data["tunein"] = "YES"

    with open(args.file, 'w') as outfile:
        json.dump(data, outfile)

    if args.debug:
        print "===> json data"
        pp.pprint(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send data to Tunein and update json file')
    parser.add_argument("file", help="json file")
    parser.add_argument("--debug", help="enable debugging output", \
                        action="store_true")
    args = parser.parse_args()

    main(args)

