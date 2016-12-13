#!/usr/bin/env python3
import argparse
import glob
import json
import re
import requests
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-k', '--api-key',
        help='API key'
    )
    parser.add_argument('--id')
    parser.add_argument('--limit', type=int, help="Max number of videos to handle (defaults to 1)", default=1)
    args = parser.parse_args()
    if not args.api_key:
        parser.print_help()
        sys.exit(1)

    if args.id:
        process(args.api_key, args.id)
        sys.exit(0)

    for filename in glob.glob("data/videos/*/*.json"):
        if args.limit <= 0:
            break
        print(filename)
        with open(filename) as fh:
            video = json.loads(fh.read())
            #if not video['speakers']:
            #    continue 
            if 'length' in video and video['length']:
                continue
            if video['videos'][0]['type'] == 'youtube':
                resp = process(args.api_key, video['videos'][0]['code'])
                #print(resp)
                for k in resp:
                    video[k] = resp[k]
                #print(video)
                with open(filename, 'w') as fh:
                    json.dump(video, fh, sort_keys=True, indent=4, separators=(',', ': '))
                args.limit -= 1

    #parser.print_help()
    #sys.exit(1)


def process(api_key, vid):
    url = 'https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails&key={}&id={}'.format(api_key, vid)
    #print(url)
    response = requests.get(url).json()
    #print(response)
    # {'items': [], 'kind': 'youtube#videoListResponse', 'etag': '"gMxXHe-zinKdE9lTnzKu8vjcmDI/q9wh51deRpP1b7X8Nc3D-bdBxqs"', 'pageInfo': {'resultsPerPage': 0, 'totalResults': 0}}
    # {'kind': 'youtube#videoListResponse', 'items': [{'kind': 'youtube#video', 'id': 'yU2jrAoBA0A', 'statistics': {'commentCount': '0', 'viewCount': '53', 'dislikeCount': '0', 'favoriteCount': '0', 'likeCount': '1'}, 'etag': '"gMxXHe-zinKdE9lTnzKu8vjcmDI/T454RL0jcXdgxzeiQbllTRN-SZ4"', 'contentDetails': {'projection': 'rectangular', 'dimension': '2d', 'duration': 'PT18M40S', 'licensedContent': False, 'caption': 'false', 'definition': 'hd'}}], 'etag': '"gMxXHe-zinKdE9lTnzKu8vjcmDI/Pka3iB8TN8iBP4E9pXHZQUKKYZ4"', 'pageInfo': {'totalResults': 1, 'resultsPerPage': 1}}
    if response['pageInfo']['totalResults'] == 0:
        raise(Exception("Data not found for {}".format(vid)))
    elif response['pageInfo']['totalResults'] > 1:
        raise(Exception("More than one responses for {}".format(vid)))
    else:
        stats = response['items'][0]['statistics']
        details = response['items'][0]['contentDetails']
        duration = details['duration'] # 'PT18M40S'  'PT1H6M57S'
        match = re.search(r'^PT((?P<hour>\d?\d)H)?((?P<min>\d\d?)M)?((?P<sec>\d\d?)S)?$', duration)
        if not match:
            raise Exception("Unknown duration format: '{}' in {}".format(duration, vid))

        length = ''
        if match.group('hour'):
            length = match.group('hour').zfill(2) + ':'
        minutes = match.group('min')
        if not minutes:
            minutes = '00'
        length += minutes.zfill(2) + ':'
        sec = match.group('sec')
        if not sec:
            sec = '00'
        length += sec.zfill(2)

        return {
            'views'    : stats['viewCount'],
            'likes'    : stats.get('likeCount', 0),
            'favorite' : stats.get('favoriteCount', 0),
            'length'   : length,
        }
main()

# vim: expandtab
