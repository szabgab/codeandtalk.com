#!/usr/bin/env python3
import json
import glob
import sys

# TODO: allow me to list only videos with speakers and/or only videos without speaker

def _in_sec(length):
    parts = [int(x) for x in length.split(':')]
    sec = 0
    #print(parts)
    while len(parts) > 0:
        sec *= 60
        sec += parts.pop(0)
    return sec

def main():
    if len(sys.argv) == 2:
        max_length = _in_sec(sys.argv[1])
        min_length = 0;
    elif len(sys.argv) == 3:
        min_length = _in_sec(sys.argv[1])
        max_length = _in_sec(sys.argv[2])
    else:
        exit("{} MM::SS [MM::SS]".format(sys.argv[0]))

    videos = []
    for video_file in glob.glob("data/videos/*/*.json"):
        with open(video_file) as fh:
            video = json.load(fh)
            if 'featured' in video:
                continue
            if 'skipped' in video:
                continue

            # show only videos with people?
            if not video['speakers']:
                continue

            if 'length' in video:
                sec = _in_sec(video['length'])
                if min_length < sec < max_length:
                    videos.append({
                        'filename': video_file,
                        'length'  : video['length'],
                        'sec'     : sec,
                    })
    
    for video in sorted(videos, key=lambda v: v['sec']):
        #exit(video)
        print("{} {}".format(video['length'], video['filename']))

main()

# vim: expandtab
