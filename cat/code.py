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
import logging

from cat import tools
class CATerror(Exception):
    pass

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
    for k in tr.keys():
        t = re.sub(k, tr[k], t)
    t = re.sub(r'[.+ ()&/:]', '-', t)
    if re.search(r'[^a-z0-9-]', t):
        raise CATerror("Characters of '{}' need to be mapped in 'cat/chars.csv'".format(t))
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return t

def html2txt(html):
    #text = re.sub(r'<a\s+href="[^"]+">([^<]+)</a>', '$1', html)
    text = re.sub(r'</?[^>]+>', '', html)
    return text


class GenerateSite(object):
    def __init__(self):
        logging.basicConfig(filename='generate.log', level=logging.DEBUG)

        self.errors = []
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.now = datetime.now().strftime('%Y-%m-%d')
        self.people = {}
        self.redirects = []
        self.people_search = {}
        self.tags = {}
        self.blasters = []
        self.html = os.path.join(self.root, 'html')
        self.data = os.path.join(self.root, 'data')
        if 'CAT_TEST' in os.environ:
            self.data = os.path.join(self.root, os.environ['CAT_TEST'])
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

        with open(os.path.join(self.data, 'locations.json'), encoding="utf-8") as fh:
            self.locations = json.load(fh)

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
        with open(os.path.join(self.html, 'cat.json'), 'w', encoding="utf-8") as fh:
            json.dump(cat, fh)
        if len(sys.argv) > 1:
            for e in cat.keys():
                with open(os.path.join(self.html, e + '.json'), 'w', encoding="utf-8") as fh:
                    json.dump(cat[e], fh)


    def read_sources(self):
        self.sources = []
        sources_file = os.path.join(self.data, 'sources.json')
        if os.path.exists(sources_file):
            with open(sources_file, encoding="utf-8") as fh:
                self.sources = json.load(fh)
        else:
            logging.info('sources file {} is missing'.format(sources_file))


    def read_tags(self):
        with open(os.path.join(self.data, 'tags.json'), encoding="utf-8") as fh:
                self.tags = json.load(fh)
                for tag in self.tags:
                    self.tags[ tag ]['episodes'] = []
                    for f in ['videos', 'total', 'future']:
                        self.tags[ tag ][f] = 0
        return

    def read_blasters(self):
        blasters_file = os.path.join(self.data, 'blasters.csv')
        if os.path.exists(blasters_file):
            with open(blasters_file, encoding="utf-8") as fh:
                rd = csv.DictReader(fh, delimiter=';')
                for row in rd:
                    self.blasters.append(row)
        else:
            logging.info('blasters file {} is missing'.format(blasters_file))

        return

    def read_events(self):

        for filename in glob.glob(os.path.join(self.data, 'events', '*')):
            logging.info('processing {}'.format(filename))
            # allow for "commenting out" files by adding a _ prefix
            if os.path.basename(filename).startswith('_'):
                continue
            if filename[-5:] != '.json':
                self.errors.append('ERROR 7: filename is not .json file. "{}"'.format(filename))
                continue
            if filename[len(self.data):] != filename[len(self.data):].lower():
                self.errors.append('ERROR 6: filename is not all lower case. "{}"'.format(filename))
            if not re.search('^[a-z0-9-]+\.json$', os.path.basename(filename)):
                self.errors.append('ERROR 8: filename has characters that are not accepted (a-z0-9-). "{}"'.format(os.path.basename(filename)))
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

                self.check_dates(this, filename)

                # verify year in filename. Won't be needed after the merge of series
                event_year = this['event_start'][0:4]
                try:
                    nickname.index(event_year)
                except ValueError:
                    self.errors.append('ERROR 9: Invalid file name. Should contain the year "{}". In file "{}".'.format(event_year, filename))

                self.check_fields(this, filename)
                self.check_name(this, filename)
                self.check_website(this, filename)
                self.check_diversity(this, filename)
                self.check_social(this, filename)
                self.check_location(this, filename)
                self.check_tags(this, filename)
                self.check_comments(this, filename)
                self.events[ this['nickname'] ] = this
            except json.decoder.JSONDecodeError as e:
                self.errors.append("ERROR 54: JSON Parsing error in {}. Details: {}".format(filename, e))
            except CATerror:
                raise
#            except Exception as e:
#                raise CATerror("ERROR 1: Unhandled error: {} in file {}".format(e, filename))
        if self.errors != []:
            raise CATerror('\n'.join(self.errors))
        return

    def check_fields(self, this, filename):
        valid_fields = set([
            'accessibility',
            'cfp_end',
            'cfp_class',           # ???
            'code_of_conduct',
            'comment',
            'description',
            'diversitytickets',
            'diversitytickets_text',
            'diversitytickets_url',
            'event_end',
            'event_start',
            'facebook',
            'file_date',            # added
            'github',
            'hashtag',
            'languages',
            'location',
            'name',
            'nickname',
            'private_comments',
            'tags',
            'twitter',
            'youtube',
            'videos_url',
            'vimeo',
            'website',
        ])
        current_fields = set(this.keys())
        if not current_fields.issubset(valid_fields):
            self.errors.append('ERROR 52: Invalid fields {}. {}'.format(current_fields - valid_fields, filename))

    def check_comments(self, this, filename):
        if 'private_comments' in this:
            if this['private_comments'].__class__.__name__ != 'str':
                self.errors.append('ERROR 51: The "private_comments" field must be a simple string. {}'.format(filename))

    def check_name(self, this, filename):
       if 'name' not in this or this['name'] == '':
           self.errors.append('ERROR 15: Missing or empty "name" field in {}'.format(filename))
           return
       if re.search(r'\d\d\d\d\s*$', this['name']):
           self.errors.append('ERROR 16: The conference "name" should not include the year. Seen in {}'.format(filename))


    def check_website(self, this, filename):
       if 'website' not in this or not re.search(r'^https?://.{8}', this['website']):
           self.errors.append('ERROR 17: Missing or invalid "website" field in {}'.format(filename))

    def check_dates(self, this, filename):
        date_format =  r'^\d\d\d\d-\d\d-\d\d$'
        for f in ['event_start', 'event_end', 'cfp_end']:
            if f in this and this[f] and not re.search(date_format, this[f]):
                self.errors.append('ERROR 22: Invalid {} {} in {}'.format(f, this[f], filename))

        start_date = datetime.strptime(this['event_start'], '%Y-%m-%d')
        end_date = datetime.strptime(this['event_end'], '%Y-%m-%d')
        if end_date < start_date :
            self.errors.append('ERROR 23: Invalid event dates (Start after End) in {}'.format(filename))

        if 'cfp_end' in this and this['cfp_end']:
            cfp_date = datetime.strptime(this['cfp_end'], '%Y-%m-%d')
            if cfp_date > start_date:
                self.errors.append('ERROR 24: Invalid CFP date (CFP after Start) in {}'.format(filename))

        this['cfp_class'] = 'cfp_none'
        cfp = this.get('cfp_end', '')
        if cfp != '':
            if cfp < self.now:
                this['cfp_class'] = 'cfp_past'
            else:
                this['cfp_class'] = 'cfp_future'

    def check_diversity(self, this, filename):
        diversity = this.get('diversitytickets')
        if diversity:
            if not re.search(r'^\d+$', diversity):
                self.errors.append('ERROR 25: diversitytickets must be a number. Use diversitytickets_url and diversitytickets_text for alternatives {} in {}'.format(this, filename))

        code_of_conduct = this.get('code_of_conduct')
        if code_of_conduct:
            if this['code_of_conduct'].__class__.__name__ != 'str':
                self.errors.append('ERROR 631: "code_of_conduct" needs to be a single string and not {} in {}'.format(this['code_of_conduct'], filename))
                return

    def check_social(self, this, filename):
        if 'twitter' in this and this['twitter'] != '':
            if not re.search(r'^[a-zA-Z0-9_]+$', this['twitter']):
                self.errors.append('ERROR 26: Invalid twitter handle "{}" in {}'.format(this['twitter'], filename))

        if 'youtube' in this and this['youtube'] != '' and this['youtube'] != '-':
            #if not re.search(r'^P[a-zA-Z0-9_-]+$', this['youtube']):
            if re.search(r'https?://', this['youtube']):
                self.errors.append('ERROR 27: Invalid youtube playlist "{}" in {}'.format(this['youtube'], filename))

        if 'facebook' in this and this['facebook'] != '':
            if not re.search(r'^https?://www.facebook.com/', this['facebook']):
                self.errors.append('ERROR 28: Invalid facebook entry "{}" in {}. Include entire Facebook URL.'.format(this['facebook'], filename))

        if 'hashtag' in this and this['hashtag'] != '':
            if this['hashtag'].__class__.__name__ != 'str':
                self.errors.append('ERROR 531: Hashtag needs to be a single string and not {} in {}'.format(this['hashtag'], filename))
                return
            if not re.search(r'^[אפa-zA-Z0-9_]+$', this['hashtag']):
                self.errors.append('ERROR 53: Invalid hashtag handle "{}" in {}'.format(this['hashtag'], filename))
                return



    def check_location(self, this, filename):
        if 'location' not in this or not this['location']:
            self.errors.append('ERROR 21: The "location" field is missing. See docs/EVENTS.md. In file {}.'.format(filename))
            return
        location = this['location']

        if 'city' not in location or not location['city']:
            self.errors.append('ERROR 18: The "city" field is missing. See docs/EVENTS.md. In file {}.'.format(filename))

        if not 'country' in location or not location['country']:
            self.errors.append('ERROR 20: The "country" field is missing. See docs/EVENTS.md. In file {}.'.format(filename))
            return

        if location['country'] not in self.locations:
            self.errors.append('ERROR 13: The value of country "{}" is not in our list. If this was not a typo, add it to data/locations.json. Found in {}'.format(location['country'], filename))
            return

        city_name = '{}, {}'.format(location['city'], location['country'])
        city_page = topic2path('{} {}'.format(location['city'], location['country']))

        # In some countries we require a state:
        # verify that the country/state/city exists as required and they are from the expected values
        if location['country'] in ['Australia', 'Brasil', 'Canada', 'India', 'USA', 'UK']:
            if 'state' not in location or not location['state']:
                self.errors.append('ERROR 19: The "state" field is missing. See docs/EVENTS.md. In file {}.'.format(filename))
            else:
                if location['state'] not in self.locations[ location['country'] ]:
                    self.errors.append('ERROR 12: The value of state "{}" is not in our list. If this was not a typo, add it to data/locations.json. Found in {}'.format(location['state'], filename))
                else:
                    if location['city'] not in self.locations[ location['country'] ][ location['state'] ]:
                        self.errors.append('ERROR 10: The value of city "{}" is not in our list. If this was not a typo, add it to data/locations.json. Found in {}'.format(location['city'], filename))

            city_name = '{}, {}, {}'.format(location['city'], location['state'], location['country'])
            city_page = topic2path('{} {} {}'.format(location['city'], location['state'], location['country']))
        else:
            #if 'state' in location and location['state']:
            #    self.errors.append('State {} should not be in {}'.format(location['state'], this))
            if location['city'] not in self.locations[ location['country'] ]:
                self.errors.append('ERROR 11: The value of city "{}" is not in our list. If this was not a typo, add it to data/locations.json. Found in {}'.format(location['city'], filename))
   

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

    def check_tags(self, this, filename):
        my_topics = []
        #print(this)
        if 'tags' not in this:
            self.errors.append('ERROR 29: tags missing from {}'.format(p))
            return
        for t in this['tags']:
            if t not in self.tags:
                self.errors.append('ERROR 14: Tag "{}" is not in the list of tags found in data/tags.json. Check for typo. Add new tags if missing from our list. in file {}'.format(t, filename))
            my_topics.append({
                'name' : t,
                'path' : t,
            })
        this['topics'] = my_topics

        for tag in this['topics']:
            p = tag['path']
            if p not in self.tags:
                self.errors.append('ERROR 30: Missing tag "{}"'.format(p))
                continue
            #self.tags[p]['events'].append(this)
            self.tags[p]['total'] += 1
            if this['event_start'] >= self.now:
                self.tags[p]['future'] += 1
            #self.stats['tags'][p]['total'] += 1
            #if this['event_start'] >= self.now:
            #    self.stats['tags'][p]['future'] += 1


    def read_people(self):
        path = os.path.join(self.data, 'people')

        for filename in glob.glob(os.path.join(path, '*.json')):
            if filename[len(self.root):] != filename[len(self.root):].lower():
                self.errors.append('ERROR 31: filename is not all lower case. "{}"'.format(filename))
            try:
                this = {}
                nickname = os.path.basename(filename)
                nickname = nickname[0:-5]
                with open(filename, encoding="utf-8") as fh:
                    this = json.load(fh)
                    for f in this:
                        if f == 'description':
                            continue
                        if f == 'topics':
                            for t in this[f]:
                                if re.search(r'\s\Z', t):
                                    self.errors.append('ERROR 32: Trailing space in "{}" {}'.format(f, filename))
                                if re.search(r'\A\s', t):
                                    self.errors.append('ERROR 33: Leading space in "{}" {}'.format(f, filename))
                            continue
                        if re.search(r'\s\Z', this[f]):
                            self.errors.append('ERROR 34: Trailing space in "{}" {}'.format(f, filename))
                        if re.search(r'\A\s', this[f]):
                            self.errors.append('ERROR 35: Leading space in "{} {}'.format(f, filename))

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

                self.people_search[nickname] = person
            except CATerror:
                raise
            except Exception as e:
                self.errors.append("ERROR 2: Unhanded error: {} in file {}".format(e, filename))

        return

    def read_series(self):
        with open(os.path.join(self.data, 'series.json'), encoding="utf-8") as fh:
            self.series = json.load(fh)
            for s in self.series:
                if s == '':
                    raise CATerror('ERROR 36: Empty key in series {}'.format(self.series[s]))

    def read_videos(self):
        self.videos = []
        path = os.path.join(self.data, 'videos')
        if not os.path.exists(path):
            return;
        events = os.listdir(path)
        for event in events:
            dir_path = os.path.join(path, event)
            for video_file_path in glob.glob(os.path.join(dir_path, '*.json')):
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
                        raise CATerror('ERROR 37: There was an exception reading {}\n{}'.format(video_file_path, e))

                # Make sure we have a length field
                if 'length' not in video:
                    raise CATerror('ERROR 38: Video {}/{}.json was featured but has no length'.format(self.events[ video['event'] ]['nickname'], video['filename']))
                if video['length'] == '':
                    raise CATerror('ERROR 39: Video {}/{}.json was featured but had empty length'.format(self.events[ video['event'] ]['nickname'], video['filename']))
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
            file = os.path.join(self.data, 'podcasts', src['name'] + '.json')
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
                        raise CATerror("ERROR 3: Could not read in {} {}".format(file, e))

        for e in self.episodes:
            #print(e)
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
                        raise CATerror('ERROR 40: Missing tag "{}"'.format(path))
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
                #self.errors.append('ERROR 41: Event without series: {}'.format(event['nickname']))
                other.append(event)

        for s in self.series.keys():
            self.series[s]['events'].sort(key=lambda x: x['event_start'])
            if self.series[s]['events'] == []:
                self.errors.append('ERROR 91: Series without event: {}'.format(s))

        if self.errors != []:
            raise CATerror('\n'.join(self.errors))
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
                    raise CATerror('ERROR 42: featured without blaster data/videos/{}/{}.json'.format(video['event']['nickname'], video['filename']))
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

                else:
                    raise CATerror('ERROR 43: Missing people file for "{}" in {}/videos/{}/{}.json'.format(s, self.data, video['event']['nickname'], video['filename']))
            video['speakers'] = speakers
            if 'tags' in video:
                for t in video['tags']:
                    p = t['link']
                    if p not in self.tags:
                        raise CATerror('ERROR 44: Missing tag "{}"'.format(p))
                    self.tags[p]['videos'] += 1

        #print(self.featured_by_blaster)

    def _process_podcasts(self):
        for e in self.episodes:
            if 'guests' in e:
                for g in e['guests']:
                    if g not in self.people:
                        raise CATerror("ERROR 4: '{}' is not in the list of people".format(g))
                    if 'episodes' not in self.people[g]:
                        self.people[g]['episodes'] = []
                    self.people[g]['episodes'].append(e)
            if 'hosts' in e:
                for h in e['hosts']:
                    if h not in self.people:
                        raise CATerror("ERROR 5: '{}' is not in the list of people".format(h))
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

        if self.stats['future'] == 0:
            self.stats['coc_future_perc']  = 0
            self.stats['diversity_tickets_future_perc']  = 0
            self.stats['a11y_future_perc'] = 0
        else:
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
                    raise CATerror('ERROR 45: Invalid field "{}" in {}'.format(f, video))
            for f in required_fields:
                if f not in video:
                    raise CATerror('ERROR 46: Mssing required field: "{}" in {}'.format(f, video))
            if not re.search(r'^\d\d\d\d-\d\d-\d\d$', video['recorded']):
                raise CATerror('ERROR 47: Invalid "recorded" field: {:20} in {}'.format(video['recorded'], video))
            if 'language' in video:
                if video['language'] not in valid_languages:
                    raise CATerror('ERROR 47: Invalid language "{}" in video data/videos/{}/{}.json'.format(video['language'], video['event'], video['filename']))
                video['title'] += ' (' + video['language'] + ')'

            if 'length' in video and video['length'] != "":
                if not re.search(r'(\d?\d:)\d\d$', video['length']):
                    raise CATerror('ERROR 48: Invalid format in length field "{}" in data/videos/{}/{}.json'.format(video['length'], video['event'], video['filename']))

    def check_people(self):
        """
            Go over all the files in the data/people directory and check if all the fields are in the list of valid_fields
        """

        valid_fields = ['name', 'github', 'twitter', 'home', 'country', 'gplus', 'nickname', 'city', 'state', 'slides', 'comment', 'topics', 'description', 'linkedin']
        for nickname in self.people.keys():
            if 'name' not in self.people[nickname]['info']:
                raise CATerror('ERROR 49: file {} does not have a "name" field'.format(nickname))
            for f in self.people[nickname]['info']:
                if f not in valid_fields:
                    raise CATerror('ERROR 50: Invlaid field "{}" in person {}'.format(f, nickname))

# vim: expandtab
