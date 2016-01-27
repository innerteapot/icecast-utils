#!/usr/bin/python2.7
#
# Update json file with icecast data
# by Joel Sutton <innerteapot@gmail.com>
#
"""
This script talks to multiple icecast servers and saves their stats to the 
nominated json file. We assume that all the servers configured are part of the
same station so we tally the total listener count. We also insert flags so that
other scripts in the collection know if they need to send data or not.
"""

__version__ = "1.1"

import argparse
import json
import os.path
import pprint
import requests
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree


def get_status(host, port, mount):
    stream_status = "UNKNOWN"
    listeners     = ""
    title         = ""
    source_ip     = ""

    u = "http://%s:%s/admin/stats.xml" % (host, port)
    a = ('admin', 'hackme')
    h = {
            'content-type': 'text/xml',
        }

    r = requests.get(u, headers=h, auth=a, timeout=5)

    tree = ElementTree.fromstring(r.content)

    for source_element in tree.iter('source'):
        if source_element.attrib["mount"] == mount:
            source_ip = ""

            for source_ip_element in source_element.iter('source_ip'):
                source_ip = source_ip_element.text

            if source_ip == "127.0.0.1":
                stream_status = "SOURCE"
            else:
                stream_status = "RELAY"

            for listeners_element in source_element.iter('listeners'):
                listeners = listeners_element.text

            for title_element in source_element.iter('title'):
                title = title_element.text

    return (stream_status, listeners, title, r)


def main(args):
    hosts = ["relay1.radio.com", "relay2.radio.com", "source.radio.com" ]
    total_listeners = 0

    if args.debug:
        print "===> Checking icecast servers"

    for h in hosts:
        (stream_status, listeners, title, r) = get_status(h, 8000, "/")

        try:
            total_listeners = total_listeners + int(listeners)

            if stream_status == "RELAY":
                total_listeners -= 1
        except ValueError:
            # don't change the total
            pass

        if stream_status == "SOURCE":
            current_track = title

            if current_track == "":
                if args.debug:
                    print h
                    print "Empty title!"
                exit(1)

    if os.path.isfile(args.file):
        with open(args.file) as json_file:
            data = json.load(json_file)
    else:
        data = {}
        data["track_history"] = []
        data["tweeted"] = "NO"
        data["slack"] = "NO"
        data["tunein"] = "NO"

    data["current_track"] = current_track
    data["total_listeners"] = total_listeners
    if len(data["track_history"]) < 1:
        data["track_history"].extend([current_track])
    else:
        if data["track_history"][-1] != current_track:
            data["track_history"].extend([current_track])
            data["tweeted"] = "NO"
            data["slack"] = "NO"
            data["tunein"] = "NO"
    data["track_history"] = data["track_history"][-10:]

    with open(args.file, 'w') as outfile:
        json.dump(data, outfile)

    if args.debug:
        pp = pprint.PrettyPrinter(indent=4)
        print "===> json data saved"
        pp.pprint(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update json file with icecast data')
    parser.add_argument("file", help="json file")
    parser.add_argument("--debug", help="enable debugging output", \
                        action="store_true")
    args = parser.parse_args()

    main(args)

