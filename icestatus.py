#!/usr/bin/python2.7
#
# Icecast Status
# by Joel Sutton <innerteapot@gmail.com>
#
"""
This script talks to multiple icecast servers and reports back with some stats. We
assume that all the servers configured are part of the same station so we tally 
the total listener count.
"""

__version__ = "1.1"

import argparse
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

    for h in hosts:
        print "===> %s" % h
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

        if args.debug:
            print(r.url)
            print(r)
        print(stream_status)
        print(listeners)
        if args.debug:
            print(title)

    print "===> Summary"
    print "Current Track: %s" % current_track
    print "Total Listeners: %d" % total_listeners


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display icecast server stats')
    parser.add_argument("--debug", help="enable debugging output", \
                        action="store_true")
    args = parser.parse_args()

    main(args)

