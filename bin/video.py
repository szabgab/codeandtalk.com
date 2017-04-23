#!/usr/bin/env python3

import os, sys, json, datetime

# read all the events
# list the ones that have youtube value which is not - and that does NOT have the video directory.
# list the ones that have no youtube entry or that it is empty
# Only show events that have already finished.

with open(os.path.join('html', 'cat.json')) as fh:
    cat = json.load(fh)

now = datetime.datetime.now()
now_str = now.strftime('%Y-%m-%d')

no_videos = ''
no_youtube = ''
on_vimeo = ''
for e in sorted(cat['events'].values(), key=lambda e: e['event_start'], reverse=True):
    #exit(e)
    if e.get('videos_url'):
        continue

    youtube = e.get('youtube')
    vimeo = e.get('vimeo')

    if e['event_end'] > now_str:
        if youtube:
            exit("ERROR. There is a youtube entry in a future event {}".format(e['nickname']))
        continue

    if youtube:
        if youtube != '-':
            if not os.path.exists('data/videos/' + e['nickname']):
                no_videos += "--list {:30} -d {} -e {}\n".format( youtube, e['event_start'], e['nickname'])
    elif vimeo:
        on_vimeo += "vimeo {} {}\n".format( e['event_start'], e['nickname'] )
    else:
        no_youtube += "{} {}\n".format( e['event_start'], e['nickname'] )

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

