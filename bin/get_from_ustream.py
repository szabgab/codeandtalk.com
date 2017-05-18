#!/usr/bin/env python3
import argparse
import json
import os
from pyquery import PyQuery
import re
import requests

# given a URL such as http://www.ustream.tv/recorded/102894434
# fetch the details of the presentation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',  help='URL of the video: http://www.ustream.tv/recorded/102894434', required=True)
    parser.add_argument('-d', '--date', help='date in YYYY-MM-DD format', required=True)
    parser.add_argument('-e', '--event', help='date in YYYY-MM-DD format', required=True)
    args = parser.parse_args()

    print(args.url)
    print(args.date)
    print(args.event)

    response = requests.get(args.url)
    if response.status_code != 200:
        print("Failed to fetch {}".format(args.url))
        return

    m = re.search(r'\d+$', args.url)
    video_code = m.group(0)
    print(video_code)

    event_dir = 'data/videos/{}'.format(args.event)
    print(event_dir)
    if not os.path.exists(event_dir):
        os.mkdir(event_dir)

    html = PyQuery(response.content)
    # speaker - title
    # <meta property="og:title" content="Patrick Kua - Tech Lead Skills for Developers" />
    speaker_title = html('meta[@property="og:title"]')[0].attrib['content']
    speaker, title  = speaker_title.split(' - ', 2)
#    print(speaker)
#    print(title)
    #re.sub(r'', '-', title.lower())

    speaker_nickname = re.sub(r' +', '-', speaker.lower())
    print(speaker_nickname)
    speaker_file = "data/people/{}.txt".format(speaker_nickname)
    if not os.path.exists(speaker_file):
        with open(speaker_file, 'w') as fh:
            fh.write("name: {}\n".format(speaker))

    event_file = "{}/{}.json".format(event_dir, video_code)
    print(event_file)

    data = {
        "description" : html('meta[@property="og:description"]')[0].attrib['content'],
        "favorite": "0",
        "length": "",
        "likes": "0",
        "recorded": args.date,
        "speakers": [
            speaker_nickname
        ],
        "tags": [],
        # <meta property="og:image" content="http://static-cdn1.ustream.tv/i/video/picture/0/1/102/102894/102894434/1_17590738_102894434,640x360,b,1:2.jpg" />
        "thumbnail_url": html('meta[@property="og:image"]')[0].attrib['content'],
        "title": title,
        "videos": [
            {
                "code": video_code,
                "type": "ustream"
            }
        ],
        "views": "0"
    }

    #import code
    #video_code.interact(local=locals())

    #m = html('meta["property="og:description"]')
    #print(m.html)
    if os.path.exists(event_file):
        print("File {} already exists.".format(event_file))
        return

    with open(event_file, 'w') as fh:
        json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '))

    print("length is missing! Add it manually!")

main()

# vim: expandtab

