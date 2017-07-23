import csv
import copy
from datetime import datetime
import glob
import json
import os
import re
import urllib
import sys
#import string
from jinja2 import Environment, PackageLoader

from cat import tools


def read_chars():
    tr = {}
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, 'cat', 'chars.csv'), encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter=',') 
        for row in rd:
            tr[row[0]] = row[1]
    return tr
tr = read_chars()
 
def topic2path(tag):
    t = tag.lower()
    if t == 'c++':
        return t
    #t = t.translate(string.maketrans("abc", "def"))
    if sys.platform in ['darwin', 'linux', 'linux2']:
        for k in tr.keys():
            t = re.sub(k, tr[k], t)
    else:  # special case for Windows...
        t = re.sub(r'[^a-zA-Z0-9]', '', t)
    t = re.sub(r'[.+ ()&/:]', '-', t)
    if re.search(r'[^a-z0-9-]', t):
        raise Exception("Characters of '{}' need to be mapped in 'cat/chars.csv'".format(t))
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return t

def html2txt(html):
    #text = re.sub(r'<a\s+href="[^"]+">([^<]+)</a>', '$1', html)
    text = re.sub(r'</?[^>]+>', '', html)
    return text


def new_tag(t):
    return {
        'name' : t,
        #'events' : [],
        'videos' : 0,
        'episodes' : [],
        'total' : 0,
        'future' : 0,
    }

class GenerateSite(object):
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.now = datetime.now().strftime('%Y-%m-%d')
        self.people = {}
        self.redirects = []
        self.people_search = {}
        self.tags = {}
        self.blasters = []
        self.html = os.path.join(self.root, 'html')
        self.data = os.path.join(self.root, 'data')
        self.featured_by_blaster = {}
        self.featured_by_date = {}
        self.events = {}
 
        self.stats = {
            'has_coc' : 0,
            'has_coc_future' : 0,
            'has_a11y' : 0,
            'has_a11y_future' : 0,
            'has_diversity_tickets' : 0,
            'has_diversity_tickets_future' : 0,
            'cities'    : {},
            'countries' : {},
            #'tags'      : {},
        }

    def read_all(self):
        self.read_sources()
        self.read_tags()
        self.read_blasters()
        self.read_events()
        self.read_series()
        self.read_people()
        self.read_videos()
        self.read_podcast_episodes()


    def process_videos(self):
        for video in self.videos:
            short_description = html2txt(video.get('description', ''))
            short_description = re.sub(r'"', '', short_description)
            short_description = re.sub(r'\s+', ' ', short_description)
            video['short_description'] = short_description
            limit = 128
            if len(short_description) > 128:
                video['short_description'] =  short_description[0:limit]
    
    def generate_site(self):
        self.read_all()

        self.stats['podcasts'] = len(self.sources)
        self.stats['people']   = len(self.people)
        self.stats['episodes'] = sum(len(x['episodes']) for x in self.sources)

        self.check_people()
        self.check_videos()

        self.process_videos()

        cat = {
            'people'   : copy.deepcopy(self.people),
            'videos'   : copy.deepcopy(self.videos),
            'blasters' : copy.deepcopy(self.blasters),
        }

        self.preprocess_events()

        cat['events'] =  copy.deepcopy(self.events)
        cat['tags']  = copy.deepcopy(self.tags)
        cat['stats'] = copy.deepcopy(self.stats)
        cat['series'] = copy.deepcopy(self.series)
        cat['podcasts'] = copy.deepcopy(self.sources)
        self.save_all(cat)

    def save_all(self, cat):
        with open(self.html + '/cat.json', 'w', encoding="utf-8") as fh:
            json.dump(cat, fh)
        if len(sys.argv) > 1:
            for e in cat.keys():
                with open(self.html + '/' + e + '.json', 'w', encoding="utf-8") as fh:
                    json.dump(cat[e], fh)


    def read_sources(self):
        with open(self.data + '/sources.json', encoding="utf-8") as fh:
            self.sources = json.load(fh)


    def read_tags(self):
        with open(self.data + '/tags.csv', encoding="utf-8") as fh:
            rd = csv.DictReader(fh, delimiter=';')
            for row in rd:
                path = topic2path(row['name'])
                self.tags[ path ] = new_tag(row['name'])
                #self.stats['tags'][path] = {
                #    'total'  : 0,
                #    'future' : 0,
                #}
        return

    def read_blasters(self):
        with open(self.data + '/blasters.csv', encoding="utf-8") as fh:
            rd = csv.DictReader(fh, delimiter=';')
            for row in rd:
                self.blasters.append(row)
        return

    def read_events(self):
        countries = []
        with open(os.path.join(self.root, 'data', 'countries.csv'), encoding="utf-8") as fh:
            for line in fh:
                name, continent = line.rstrip("\n").split(",")
                countries.append(name)

        for filename in glob.glob(self.data + '/events/*.json'):
            if filename[len(self.root):] != filename[len(self.root):].lower():
                raise Exception("filename '{}' is not all lower case".format(filename))
            #print("Reading {}".format(filename))
            conf = {}
            try:
                with open(filename, encoding="utf-8") as fh:
                    this = json.load(fh)

                nickname = os.path.basename(filename)
                nickname = nickname[0:-5]
                #print(nickname)
                this['nickname'] = nickname
                this['file_date'] = datetime.fromtimestamp( os.path.getctime(filename) ).strftime('%Y-%m-%d')

                date_format =  r'^\d\d\d\d-\d\d-\d\d$'
                for f in ['event_start', 'event_end', 'cfp_end']:
                    if f in this and this[f] and not re.search(date_format, this[f]):
                        raise Exception('Invalid {} {} in {}'.format(f, this[f], filename))

                start_date = datetime.strptime(this['event_start'], '%Y-%m-%d')
                end_date = datetime.strptime(this['event_end'], '%Y-%m-%d')
                if end_date < start_date :
                    raise Exception('Invalid event dates (Start after End) in {}'.format(filename))

                if 'cfp_end' in this and this['cfp_end']:
                    cfp_date = datetime.strptime(this['cfp_end'], '%Y-%m-%d')
                    if cfp_date > start_date:
                        raise Exception('Invalid CFP date (CFP after Start) in {}'.format(filename))

                event_year = this['event_start'][0:4]
                if not this['name'].endswith(event_year):
                    raise Exception('Invalid event name {}. Should end with year \'{}\''.format(this['name'], event_year))

                if not 'location' in this or not this['location']:
                    raise Exception('Location is missing from {}'.format(this))
                location = this['location']
                if not 'country' in location or not location['country']:
                    raise Exception('Country is missing from {}'.format(this))
                if location['country'] not in countries:
                    raise Exception("Country '{}' is not yet(?) in our list".format(location['country']))

                diversity = this.get('diversitytickets')
                if diversity:
                    if not re.search(r'^\d+$', diversity):
                        raise Exception('diversitytickets must be a number. Use diversitytickets_url and diversitytickets_text for alternatives {}'.format(this))

                my_topics = []
                #print(this)
                if 'tags' not in this:
                    raise Exception("tags missing from {}".format(p))
                for t in this['tags']:
                    if t not in self.tags:
                        raise Exception("Tag '{}' is not in the list of tags".format(t))
                    my_topics.append({
                        'name' : t,
                        'path' : t,
                    })
                this['topics'] = my_topics

                if 'twitter' in this and this['twitter'] != '':
                    if not re.search(r'^[a-zA-Z0-9_]+$', this['twitter']):
                        raise Exception("Invalid twitter handle '{}' in {}".format(this['twitter'], filename))

                if 'youtube' in this and this['youtube'] != '' and this['youtube'] != '-':
                    #if not re.search(r'^P[a-zA-Z0-9_-]+$', this['youtube']):
                    if re.search(r'https?://', this['youtube']):
                        raise Exception("Invalid youtube playlist '{}' in {}".format(this['youtube'], filename))


                this['cfp_class'] = 'cfp_none'
                cfp = this.get('cfp_end', '')
                if cfp != '':
                    if cfp < self.now:
                        this['cfp_class'] = 'cfp_past'
                    else:
                        this['cfp_class'] = 'cfp_future'

                if 'location' not in this or not this['location']:
                    raise Exception("Location is missing from {}".format(this))
                location = this['location']
                if 'city' not in location or not location['city']:
                    raise Exception("City is missing from {}".format(location))
                city_name = '{}, {}'.format(location['city'], location['country'])
                city_page = topic2path('{} {}'.format(location['city'], location['country']))
                # In some countries we require a state:
                if location['country'] in ['Australia', 'Brasil', 'India', 'USA']:
                    if 'state' not in location or not location['state']:
                        raise Exception('State is missing from {}'.format(this))
                    city_name = '{}, {}, {}'.format(location['city'], location['state'], location['country'])
                    city_page = topic2path('{} {} {}'.format(location['city'], location['state'], location['country']))
                this['city_name'] = city_name
                this['city_page'] = city_page

                if city_page not in self.stats['cities']:
                    self.stats['cities'][city_page] = {
                        'name' : city_name,
                        'total' : 0,
                        'future' : 0,
                    }
                self.stats['cities'][city_page]['total'] += 1
                if this['event_start'] >= self.now:
                    self.stats['cities'][city_page]['future'] += 1


                country_name = location['country']
                country_page = re.sub(r'\s+', '-', country_name.lower())
                this['country_page'] = country_page

                if country_page not in self.stats['countries']:
                    self.stats['countries'][country_page] = {
                        'name'   : country_name,
                        'total'  : 0,
                        'future' : 0,
                    }
                self.stats['countries'][country_page]['total'] += 1
                if this['event_start'] >= self.now:
                    self.stats['countries'][country_page]['future'] += 1

                for tag in this['topics']:
                    p = tag['path']
                    if p not in self.tags:
                        raise Exception("Missing tag '{}'".format(p))
                    #self.tags[p]['events'].append(this)
                    self.tags[p]['total'] += 1
                    if this['event_start'] >= self.now:
                        self.tags[p]['future'] += 1
                    #self.stats['tags'][p]['total'] += 1
                    #if this['event_start'] >= self.now:
                    #    self.stats['tags'][p]['future'] += 1

                self.events[ this['nickname'] ] = this

            except Exception as e:
                exit("ERROR 1: {} in file {}".format(e, filename))
        return


    def read_people(self):
        path = self.data + '/people'

        for filename in glob.glob(path + "/*.txt"):
            if filename[len(self.root):] != filename[len(self.root):].lower():
                raise Exception("filename '{}' is not all lower case".format(filename)) 
            try:
                this = {}
                nickname = os.path.basename(filename)
                nickname = nickname[0:-4]
                description = None
                with open(filename, encoding="utf-8") as fh:
                    for line in fh:
                        if re.search(r'__DESCRIPTION__', line):
                            description = ''
                            continue
                        if description != None:
                            description += line
                            continue
                        
                        line = line.rstrip('\n')
                        if re.search(r'\s\Z', line):
                            raise Exception("Trailing space in '{}' {}".format(line, filename))
                        if re.search(r'\A\s*\Z', line):
                            continue
                        k,v = re.split(r'\s*:\s*', line, maxsplit=1)
                        if k in this:
                            if k == 'home':
                                # TODO: decide what to do with multiple home: entries
                                #print("Duplicate field '{}' in {}".format(k, filename))
                                pass
                            else:
                                raise Exception("Duplicate field '{}' in {}".format(k, filename))
                        this[k] = v

                if description:
                    this['description'] = description

                if 'redirect' in this:
                    self.redirects.append({
                        'from' : nickname,
                        'to'   : this['redirect'],
                    })
                    continue

                for field in ['twitter', 'github', 'home']:
                    if field not in this:
                        #print("WARN: {} missing for {}".format(field, nickname))
                        pass
                    elif this[field] == '-':
                        this[field] = None

                self.people[nickname] = {
                    'info': this,
                    #'episodes' : [],
                    #'hosting' : [],
                    #'videos'  : [],
                    #'file_date' : datetime.fromtimestamp( os.path.getctime(filename) ).strftime('%Y-%m-%d'),
                }

                person = {
                    'name'     : this['name'],
                }
                if 'country' in this:
                    person['location'] = this['country']
                if 'topics' in this:
                    person['topics']   = this['topics']
                    for t in re.split(r'\s*,\s*', this['topics']):
                        p = topic2path(t)
                        if p not in self.tags:
                            raise Exception("Topic '{}' is not in the list of tags".format(p))

                self.people_search[nickname] = person
            except Exception as e:
                exit("ERROR 2: {} in file {}".format(e, filename))

        return

    def read_series(self):
        with open(self.data + '/series.json', encoding="utf-8") as fh:
            self.series = json.load(fh)
            for s in self.series:
                if s == '':
                    raise Exception("empty key in series {}".format(self.series[s]))

    def read_videos(self):
        path = self.data + '/videos'
        events = os.listdir(path)
        self.videos = []
        for event in events:
            dir_path = os.path.join(path, event)
            for video_file_path in glob.glob(dir_path + '/*.json'):
                video_file = os.path.basename(video_file_path)
                html_file_path = video_file_path[0:-4] + 'html'

                with open(video_file_path, encoding="utf-8") as fh:
                    try:
                        video = json.load(fh)
                        video['filename'] = video_file[0:-5]
                        video['event']    = event
                        video['file_date'] = datetime.fromtimestamp( os.path.getctime(video_file_path) ).strftime('%Y-%m-%d')

                        if os.path.exists(html_file_path):
                            with open(html_file_path, encoding="utf-8") as hfh:
                                video['description'] = hfh.read()
                        self.videos.append(video)
                    except Exception as e:
                        exit("There was an exception reading {}\n{}".format(video_file_path, e))

                # Make sure we have a length field
                if 'length' not in video:
                    raise Exception("Video {}/{}.json was featured but has no length".format(self.events[ video['event'] ]['nickname'], video['filename']))
                if video['length'] == '':
                    raise Exception("Video {}/{}.json was featured but had empty length".format(self.events[ video['event'] ]['nickname'], video['filename']))
                video['l'] = tools.in_sec(video['length'])

                if 'tags' in video:
                    tags = []
                    for t in video['tags']:
                        p = topic2path(t)
                        tags.append({
                            'text': t,
                            'link': p,
                        })

                    video['tags'] = tags

 
        self.stats['videos'] = len(self.videos)
        return


    def read_podcast_episodes(self):
        self.episodes = []
        for src in self.sources:
            #print("Processing source {}".format(src['name']))
            file = self.data + '/podcasts/' + src['name'] + '.json'
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
                        self.episodes.extend(new_episodes)
                        src['episodes'] = new_episodes
                    except json.decoder.JSONDecodeError as e:
                        exit("ERROR 3: Could not read in {} {}".format(file, e))
                        src['episodes'] = [] # let the rest of the code work
                        pass

        for e in self.episodes:
            #print(e)
            #exit()
            if 'tags' in e:
                tags = []
                for tag in e['tags']:
                    path = topic2path(tag)
                    if path not in tags:
                        tags.append({
                            'text' : tag,
                            'link' : path,
                        })
                    if path not in self.tags:
                        raise Exception("Missing tag '{}'".format(path))
                        #self.tags[path] = new_tag(tag)
                    self.tags[path]['episodes'].append(e)

                e['tags'] = tags

    def _add_events_to_series(self):
        '''
            Go over all the events and based on the longest matching prefix of their filenames,
            put them in one of the entries in the series.
            To each event add the name of the series it is in.
            TODO: In the future we might add an exception if an event is not in any of the series.
        '''
        for s in self.series.keys():
            self.series[s]['events'] = []
        other = []
        for nickname in self.events.keys():
            e = self.events[nickname]
            event = {
                'nickname'   : e['nickname'],
                'name'       : e['name'],
                'event_start' : e['event_start'],
            }
            for s in sorted(self.series.keys(), key=lambda s: len(s), reverse=True):
                l = len(s)
                if event['nickname'][0:l] == s:
                    self.series[s]['events'].append(event)
                    event['series'] = s
                    e['series'] = s
                    break
            else:
                #TODO: create series for every event and then turn on the exception?
                #print("Event without series: {}".format(event['nickname']))
                #raise Exception("Event without series: {}".format(event['nickname']))
                other.append(event)

        for s in self.series.keys():
            self.series[s]['events'].sort(key=lambda x: x['event_start'])
        #self.event_in_series = {}
        #for e in self.series[s]['events']:
        #    self.event_in_series[ e['nickname'] ] = s

    def _process_videos(self):
        for b in self.blasters:
            self.featured_by_blaster[ b['file'] ] = []

        for video in self.videos:

            video['event'] = {
                'name'     : self.events[ video['event'] ]['name'],
                'nickname' : self.events[ video['event'] ]['nickname'],
                'website'  : self.events[ video['event'] ]['website'],
                'twitter'  : self.events[ video['event'] ]['twitter'],  
            }

           # collect featured videos
            featured = video.get('featured')
            blasters = video.get('blasters', [])
            if featured:

                class_name = ''
                if video['featured'] == self.now:
                    class_name = 'today_feature'
                elif video['featured'] > self.now:
                    class_name = 'future_feature'
                this_video = {
                    'class_name' : class_name,
                    'blasters'   : video['blasters'],
                    'featured'   : video['featured'],
                    'recorded'   : video['recorded'],
                    'filename'   : video['filename'],
                    'length'     : video['length'],
                    'title'      : video['title'],
                    'event'      : {
                        'nickname' : video['event']['nickname'],
                        'name'     : video['event']['name'],
                    },
                }

                if featured not in self.featured_by_date:
                    self.featured_by_date[featured] = []
                self.featured_by_date[featured].append(this_video)

                if len(blasters) == 0:
                    raise Exception("featured without blaster data/videos/{}/{}.json".format(video['event']['nickname'], video['filename']))
                for b in blasters:
                    if b not in self.featured_by_blaster:
                        self.featured_by_blaster[ b ] = []
                        #TODO mark these:
                        #print("Blaster {} is used but not in the blaster list".format(b))
                    
                    self.featured_by_blaster[b].append(this_video)
            speakers = {}
            for s in video['speakers']:
                if s in self.people:
                    speakers[s] = self.people[s]
                    #exit(video)
                    if 'videos' not in self.people[s]:
                        self.people[s]['videos'] = []

                    self.people[s]['videos'].append({
                        'recorded' : video['recorded'],
                        'title'    : video['title'],
                        # short_description
                        'event'    : video['event'],
                        'filename' : video['filename'],
                        'thumbnail_url' : video['thumbnail_url'],
                    })
                    if not 'tags' in self.people_search[s]:
                        self.people_search[s]['tags'] = set()
                    if 'tags' in video:
                        for t in video['tags']:
                            self.people_search[s]['tags'].add(t['link'])
                    #else:
                    #    TODO: shall we requre tags for each video?
                    #    exit(video)
                    
                else:
                    raise Exception("Missing people file for '{}' in {}/videos/{}/{}.json".format(s, self.data, video['event']['nickname'], video['filename']))
            video['speakers'] = speakers
            if 'tags' in video:
                for t in video['tags']:
                    p = t['link']
                    if p not in self.tags:
                        raise Exception("Missing tag '{}'".format(p))
                    self.tags[p]['videos'] += 1

        #print(self.featured_by_blaster)

    def _process_podcasts(self):
        for e in self.episodes:
            if 'guests' in e:
                for g in e['guests']:
                    if g not in self.people:
                        exit("ERROR 4: '{}' is not in the list of people".format(g))
                    if 'episodes' not in self.people[g]:
                        self.people[g]['episodes'] = []
                    self.people[g]['episodes'].append(e)
            if 'hosts' in e:
                for h in e['hosts']:
                    if h not in self.people:
                        exit("ERROR 5: '{}' is not in the list of people".format(h))
                    if 'hosting' not in self.people[h]:
                        self.people[h]['hosting'] = []
                    self.people[h]['hosting'].append(e)

    def _process_events(self):
        self.event_videos = {}
        for v in self.videos:
            if v['event']['nickname'] not in self.event_videos:
                self.event_videos[ v['event']['nickname'] ] = []
            self.event_videos[ v['event']['nickname'] ].append(v)

        for nickname in self.events.keys():
            event = self.events[nickname]


            if event['nickname'] in self.event_videos:
                event['videos'] = self.event_videos[ event['nickname'] ]


            if event.get('diversitytickets'):
                self.stats['has_diversity_tickets'] += 1
                if event['event_start'] >= self.now:
                    self.stats['has_diversity_tickets_future'] += 1
            if event.get('code_of_conduct'):
                self.stats['has_coc'] += 1
                if event['event_start'] >= self.now:
                    self.stats['has_coc_future'] += 1
            if event.get('accessibility'):
                self.stats['has_a11y']
                if event['event_start'] >= self.now:
                    self.stats['has_a11y_future'] += 1

            if 'cfp_end' in event and event['cfp_end'] >= self.now:
                tweet_cfp = 'The CfP of {} ends on {} see {} via https://codeandtalk.com/'.format(event['name'], event['cfp_end'], event['website'])
                if event['twitter']:
                    tweet_cfp += ' @' + event['twitter']
                for t in event['topics']:
                    tweet_cfp += ' #' + t['name']
                event['tweet_cfp'] = urllib.parse.quote(tweet_cfp)

            tweet_me = event['name']
            tweet_me += ' on ' + event['event_start']
            tweet_me += ' in ' + event['location']['city']
            if 'state' in event:
                tweet_me += ', ' + event['location']['state']
            tweet_me += ' ' + event['location']['country']
            if event['twitter']:
                tweet_me += ' @' + event['twitter']
            tweet_me += " " + event['website']
            for t in event['topics']:
                tweet_me += ' #' + t['name']
            #tweet_me += ' via @codeandtalk'
            tweet_me += ' via https://codeandtalk.com/'

            event['tweet_me'] = urllib.parse.quote(tweet_me)


    def preprocess_events(self):
        self.stats['total']  = len(self.events)
        self.stats['future'] = len(list(filter(lambda x: x['event_start'] >= self.now, self.events.values())))
        self.stats['cfp']    = len(list(filter(lambda x: x.get('cfp_end', '') >= self.now, self.events.values())))


        self._add_events_to_series()
        self._process_videos()
        self._process_podcasts()
        self._process_events()

        self.stats['coc_future_perc']  = int(100 * self.stats['has_coc_future'] / self.stats['future'])
        self.stats['diversity_tickets_future_perc']  = int(100 * self.stats['has_diversity_tickets_future'] / self.stats['future'])
        self.stats['a11y_future_perc'] = int(100 * self.stats['has_a11y_future'] / self.stats['future'])

        return

    def check_videos(self):
        """
            Go over all the JSON files representing videos and check validity:
               - Check if they have a "recorded" field with a YYYY-MM-DD timestamp - report if not
            TODO: Check if they have values for "speakers" - report if not
            TODO: Check if they have embedded HTML in the description field (they should be moved out to a separate file)
        """

        valid_fields = ['title', 'thumbnail_url', 'tags', 'recorded', 'description', 'videos', 'speakers', 'abstract', 'slides', 'language', 'featured', 'length', 'blasters',
            'views', 'likes', 'favorite', 'skipped', 'l']
        valid_fields.extend(['filename', 'event', 'file_date']) # generated fields
        required_fields = ['title', 'recorded']
        valid_languages = ["Hebrew", "Dutch", "Spanish", "Portuguese", "German", "French"]

        for video in self.videos:
            for f in video.keys():
                if f not in valid_fields:
                    raise Exception("Invalid field '{}' in {}".format(f, video))
            for f in required_fields:
                if f not in video:
                    raise Exception("Missing required field: '{}' in {}".format(f, video))
            if not re.search(r'^\d\d\d\d-\d\d-\d\d$', video['recorded']):
                raise Exception("Invalid 'recorded' field: {:20} in {}".format(video['recorded'], video))
            #exit(video)
            if 'language' in video:
                if video['language'] not in valid_languages:
                    raise Exception("Invalid language '{}' in video data/videos/{}/{}.json".format(video['language'], video['event'], video['filename']))
                video['title'] += ' (' + video['language'] + ')'

            if 'length' in video and video['length'] != "":
                if not re.search(r'(\d?\d:)\d\d$', video['length']):
                    raise Exception("Invalid format in length field '{}' in data/videos/{}/{}.json".format(video['length'], video['event'], video['filename']))

    def check_people(self):
        """
            Go over all the files in the data/people directory and check if all the fields are in the list of valid_fields
        """

        valid_fields = ['name', 'github', 'twitter', 'home', 'country', 'gplus', 'nickname', 'city', 'state', 'slides', 'comment', 'topics', 'description', 'linkedin']
        for nickname in self.people.keys():
            if 'name' not in self.people[nickname]['info']:
                raise Exception("file {} does not have a 'name' field".format(nickname))
            for f in self.people[nickname]['info']:
                if f not in valid_fields:
                    raise Exception("Invlaid field '{}' in person {}".format(f, nickname))

# vim: expandtab

