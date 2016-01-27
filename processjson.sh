#!/bin/bash
/root/bin/updatejson /usr/share/icecast2/web/stats.json 2>&1
/root/bin/tweetjson /usr/share/icecast2/web/stats.json 2>&1
/root/bin/slackjson /usr/share/icecast2/web/stats.json 2>&1
/root/bin/tuneinjson /usr/share/icecast2/web/stats.json 2>&1
