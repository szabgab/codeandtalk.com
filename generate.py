import argparse
from datetime import datetime
import glob
import json
import os
import sys
import re
import shutil

from xcast.people import GenerateSite

if sys.version_info.major < 3:
    exit("This code requires Python 3.\nThis is {}".format(sys.version))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', help = 'Generate HTML', action='store_true')
    parser.add_argument('--check', help = 'Check the RSS feed', action='store_true')
    parser.add_argument('--source', help = 'Check the RSS feed of given source')
    args = parser.parse_args()

    if args.source:
        check_rss_feed()
    elif args.check:
        check_rss()
    elif args.html:
        generate_html()
    else:
        parser.print_help()

def generate_html():
    root = 'html'
    if os.path.exists(root):
        shutil.rmtree(root)
    shutil.copytree('src', root)

    gs = GenerateSite()

    gs.read_tags()
    gs.read_events()
    gs.read_people()
    gs.read_videos()
    gs.read_sources()
    gs.read_episodes()

    gs.preprocess_events_once()
    gs.generate_podcast_pages()
    gs.generate_pages()

def check_rss_feed():
   source = list(filter(lambda x: x['name'] == args.source, sources))
   if not source:
       exit("'{}' is not one of the sources".format(args.source))
   #print(source[0])
   
   import feedparser
   d = feedparser.parse(source[0]['feed'])
   for e in d.entries:
       if args.source == 'floss-weekly':
           data = {}
           full_title = e['title']
           published = e['published']
           date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')  # Tue, 18 Oct 2016 10:33:51 -0700
           #comments  http://twit.tv/floss/408
           #print(e['comments'])
           #m = re.search(r'\d+$', e['comments'])
           m = re.search(r'FLOSS Weekly (\d+):\s*(.*)', full_title)
           ep = None
           if m:
               data['ep'] = m.group(1)
               data['title'] = m.group(2)
               data['permalink'] = 'https://twit.tv/shows/floss-weekly/episodes/' + data['ep']
               data['date'] = date.strftime('%Y-%m-%d')
               data['guests'] = {}
               data['hosts'] = {}
       elif args.source == 'adv-in-angular':
           print(e)
           data = {}
           full_title = e['title']
           #print(full_title) # 116 AiA Angular 2 Compiler with Tobias Bosch
           published = e['published']
           print(published)
           date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')  # Tue, 18 Oct 2016 10:33:51 -0700
           print(date)
           m = re.search(r'^\s*(\d+)\s+AiA\s+(.*) with (.*)', full_title)
           ep = None
           if m:
               data['ep'] = m.group(1)
               data['title'] = m.group(2)
           #    data['permalink'] = 'https://twit.tv/shows/floss-weekly/episodes/' + data['ep']
           #    data['date'] = date.strftime('%Y-%m-%d')
           #    data['guests'] = {}
           #    data['hosts'] = {}
           print(data)
           exit()
       else:
           exit("Cannot handle this feed")
       print(data)
       print('---')
       #exit()

   #for k in d.entries[0].keys():
   #    print("{}  {}\n".format(k, d.entries[0][k]))

def check_rss():
    import feedparser
    for s in sources:
        if 'feed' in s:
            print(s['feed'])
            d = feedparser.parse(s['feed'])
            print(d['feed']['title'])
            print(d.entries[0].title)
            print(d.entries[0].link)
            print(d.entries[0])
            print()
            exit()

        #else:
        #    print('No feed for {}'.format(s['name']))

main()

# vim: expandtab
