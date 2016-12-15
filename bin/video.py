#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite

# read all the events
# list the ones that have youtube value which is not - and that does NOT have the video directory.
# list the ones that have no youtube entry or that it is empty
# Only show events that have already finished.

gs = GenerateSite()
gs.read_tags()
gs.read_events()
no_videos = ''
no_youtube = ''
on_vimeo = ''
for e in sorted(gs.conferences, key=lambda e: e['start_date'], reverse=True):
    #exit(e)
    if e.get('videos_url'):
        continue

    youtube = e.get('youtube')
    vimeo = e.get('vimeo')

    if e['end_date'] > gs.now:
        if youtube:
            exit("ERROR. There is a youtube entry in a future event {}".format(e['nickname']))
        continue

    if youtube:
        if youtube != '-':
            if not os.path.exists('data/videos/' + e['nickname']):
                no_videos += "--list {:30} -d {} -e {}\n".format( youtube, e['start_date'], e['nickname'])
    elif vimeo:
        on_vimeo += "vimeo {} {}\n".format( e['start_date'], e['nickname'] )
    else:
        no_youtube += "{} {}\n".format( e['start_date'], e['nickname'] )

if no_videos:
    print("Has youtube ID but videos were not included")
    print(no_videos)

if on_vimeo:
    print("On vimeo")
    print(on_vimeo)

if no_youtube:
    print("Has no youtube ID")
    print(no_youtube)

# vim: expandtab

