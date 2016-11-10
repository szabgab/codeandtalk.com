import csv
from datetime import datetime
import glob
import json
import os
import re

def read_people(path):
    people = {}
    for filename in glob.glob(path + "/*.txt"):
        try:
            this = {}
            nickname = os.path.basename(filename)
            nickname = nickname[0:-4]
            with open(filename, encoding="utf-8") as fh:
                for line in fh:
                    line = line.rstrip('\n')
                    if re.search(r'\A\s*\Z', line):
                        continue
                    k,v = re.split(r'\s*:\s*', line, maxsplit=1)
                    this[k] = v
            for field in ['twitter', 'github', 'home']:
                if field not in this:
                    #print("WARN: {} missing for {}".format(field, nickname))
                    pass
                elif this[field] == '-':
                    this[field] = None
            people[nickname] = {
                'info': this,
                'episodes' : [],
                'hosting' : []
            }
        except Exception as e:
            exit("ERROR: {} in file {}".format(e, filename))

    return people

def read_tags():
    tags = {}
    with open('data/tags.csv', encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter=';') 
        for row in rd:
            path = topic2path(row['name'])
            row['path'] = path
            row['episodes'] = []
            row['events'] = []
            tags[ path ] = row
    print(tags)
    return tags

def read_videos(topics):
    root = 'data/videos'
    events = os.listdir(root)
    videos = []
    for event in events:
        path = os.path.join(root, event)
        for video_file in os.listdir(path):
            video_file_path = os.path.join(path, video_file)
            with open(video_file_path) as fh:
                video = json.load(fh)
                video['filename'] = video_file[0:-5]
                video['event']    = event
                #print(event)
                #exit()
                #print(video)
                video['file_date'] = datetime.fromtimestamp( os.path.getctime(video_file_path) )
                videos.append(video)

                if 'tags' in video:
                    tags = []
                    for t in video['tags']:
                        p = topic2path(t)
                        tags.append({
                            'text': t,
                            'link': p,
                        }) 
                        if p not in topics:
                            topics[p] = {
                                'name' : t,
                                'events' : [],
                                'videos' : [],
                                'episodes' : [],
                            }
                        topics[p]['videos'].append(video)
                    video['tags'] = tags

    return videos

def read_events(topics):
    conferences = []
    now = datetime.now().strftime('%Y-%m-%d')

    for filename in glob.glob("data/events/*.txt"):
        print("Reading {}".format(filename))
        conf = {}
        try:
            this = {}
            nickname = os.path.basename(filename)
            nickname = nickname[0:-4]
            #print(nickname)
            this['nickname'] = nickname
            this['file_date'] = datetime.fromtimestamp( os.path.getctime(filename) )
            with open(filename, encoding="utf-8") as fh:
                for line in fh:
                    line = line.rstrip('\n')
                    if re.search(r'\A\s*#', line):
                        continue
                    if re.search(r'\A\s*\Z', line):
                        continue
                    line = re.sub(r'\s+\Z', '', line)
                    k,v = re.split(r'\s*:\s*', line, maxsplit=1)
                    this[k] = v

            my_topics = []
            if this['topics']:
                for t in re.split(r'\s*,\s*', this['topics']):
                    p = topic2path(t)
                    #if p == '':
                    #    exit("ERROR {}".format(this))
                    my_topics.append({
                        'name' : t,
                        'path' : p,
                    })
                    if p not in topics:
                        topics[p] = {
                            'name': t,
                            'events' : [],
                            'videos' : [],
                            'episodes' : [],
                        }
                    topics[p]['events'].append(this)
            this['topics'] = my_topics

            this['cfp_class'] = 'cfp_none'
            cfp = this.get('cfp_date', '')
            if cfp != '':
                if cfp < now:
                    this['cfp_class'] = 'cfp_past'
                else:
                    this['cfp_class'] = 'cfp_future'

            if 'city' not in this or not this['city']:
                exit("City is missing from {}".format(this))

            city_name = '{}, {}'.format(this['city'], this['country'])
            city_page = topic2path('{} {}'.format(this['city'], this['country']))

            # In some countris we require state:
            if this['country'] in ['Australia', 'Brasil', 'India', 'USA']:
                if 'state' not in this or not this['state']:
                    exit('State is missing from {}'.format(this))
                city_name = '{}, {}, {}'.format(this['city'], this['state'], this['country'])
                city_page = topic2path('{} {} {}'.format(this['city'], this['state'], this['country']))
            this['city_name'] = city_name
            this['city_page'] = city_page

            conferences.append(this)
        except Exception as e:
            exit("ERROR: {} in file {}".format(e, filename))

    return sorted(conferences, key=lambda x: x['start_date'])

def read_episodes(sources, topics):
    episodes = []
    for src in sources:
        print("Processing source {}".format(src['name']))
        file = 'data/podcasts/' + src['name'] + '.json'
        src['episodes'] = []
        if os.path.exists(file):
            with open(file, encoding="utf-8") as fh:
                try:
                    new_episodes = json.load(fh)
                    for episode in new_episodes:
                        episode['source'] = src['name']
                        if 'ep' not in episode:
                            #print("WARN ep missing from {} episode {}".format(src['name'], episode['permalink']))
                            pass
                    episodes.extend(new_episodes)
                    src['episodes'] = new_episodes
                except json.decoder.JSONDecodeError as e:
                    exit("ERROR: Could not read in {} {}".format(file, e))
                    src['episodes'] = [] # let the rest of the code work
                    pass

    for e in episodes:
        #print(e)
        #exit()
        if 'tags' in e:
            tags = []
            for tag in e['tags']:
                path = topic2path(tag)
                if path not in tags:
                    # TODO report tag missing from the tags.csv file
                    tags.append({
                        'text' : tag,
                        'link' : path,
                    })
                if path not in topics:
                    # TODO report tag missing from the tags.csv file
                    #print(e)
                    #exit()
                    topics[path] = {
                        'name'    : tag,
                        'episodes': [],
                        'events'  : [],
                        'videos'  : [],
                    }
                topics[path]['episodes'].append(e)

            e['tags'] = tags


    return episodes


def topic2path(tag):
    t = tag.lower()
    t = re.sub(r'í', 'i', t)
    t = re.sub(r'ó', 'o', t)
    t = re.sub(r'ã', 'a', t)
    t = re.sub(r'[\W_]+', '-', t)
    return t



# vim: expandtab

