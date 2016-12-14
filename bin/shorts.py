#!/usr/bin/env python3
import json
import glob
import sys

def _in_sec(length):
    parts = [int(x) for x in length.split(':')]
    sec = 0
    #print(parts)
    while len(parts) > 0:
        sec *= 60
        sec += parts.pop(0)
    return sec

def main():
    if len(sys.argv) !=2:
        exit("{} MM::SS".format(sys.argv[0]))

    length = _in_sec(sys.argv[1])
    
    videos = []
    for video_file in glob.glob("data/videos/*/*.json"):
        with open(video_file) as fh:
            video = json.load(fh)
            if 'featured' in video:
                continue
            if 'skipped' in video:
                continue
            if 'length' in video:
                sec = _in_sec(video['length'])
                if sec < length:
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
