from datetime import datetime
import glob
import json
import os
import sys
import re
import shutil
import urllib
from jinja2 import Environment, PackageLoader

sys.path.insert(0, '../xcast')
from xcast.people import read_people

if sys.version_info.major < 3:
    exit("This code requires Python 3.\nThis is {}".format(sys.version))

def main():
    conferences, topics = read_files()
    #print(conferences)
    people = read_people('../xcast/data/people')
    videos = read_videos()
    #print(people)

    events = {}
    for e in conferences:
        events[ e['nickname'] ] = e
    for v in videos:
        v['event_name'] = events[ v['event'] ]['name']
        speakers = {}
        for s in v['speakers']:
            if s in people:
                speakers[s] = people[s]
        v['speakers'] = speakers
        #print(speakers)
        #exit()
            

    generate_pages(conferences, topics, videos, people)


def read_videos():
    root = 'videos'
    events = os.listdir(root)
    videos = []
    for event in events:
        path = os.path.join(root, event, 'videos')
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
    return videos


def read_files():
    conferences = []
    topics = {}
    now = datetime.now().strftime('%Y-%m-%d')

    for filename in glob.glob("data/*.txt"):
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
                            'events' : []
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

            conferences.append(this)
        except Exception as e:
            exit("ERROR: {} in file {}".format(e, filename))

    return sorted(conferences, key=lambda x: x['start_date']), topics

def generate_video_pages(videos, sitemap):
    root = 'html'
    env = Environment(loader=PackageLoader('conf', 'templates'))
    video_template = env.get_template('video.html')
    if not os.path.exists(root + '/v/'):
        os.mkdir(root + '/v/')
    for video in videos:
        if not os.path.exists(root + '/v/' + video['event']):
            os.mkdir(root + '/v/' + video['event'])
        #print(root + '/v/' + video['event'] + '/' + video['filename'])
        #exit()
        with open(root + '/v/' + video['event'] + '/' + video['filename'], 'w', encoding="utf-8") as fh:
            fh.write(video_template.render(
                h1          = video['title'],
                title       = video['title'],
                video       = video,
            ))
        sitemap.append({
            'url' : '/v/' + video['event'] + video['filename'],
            'lastmod' : video['file_date'],
        })
    
def generate_pages(conferences, topics, videos, people):
    root = 'html'
    if os.path.exists(root):
        shutil.rmtree(root)
    shutil.copytree('src', root)

    now = datetime.now().strftime('%Y-%m-%d')
    #print(now)

    sitemap = []
    generate_video_pages(videos, sitemap)

    stats, countries, cities = preprocess_events(now, conferences, videos)

    env = Environment(loader=PackageLoader('conf', 'templates'))

    event_template = env.get_template('event.html')
    if not os.path.exists(root + '/e/'):
        os.mkdir(root + '/e/')
    for event in conferences:
        #print(event['nickname'])

        try:
            with open(root + '/e/' + event['nickname'], 'w', encoding="utf-8") as fh:
                fh.write(event_template.render(
                    h1          = event['name'],
                    title       = event['name'],
                    event = event,
            ))
            sitemap.append({
                'url' : '/e/' + event['nickname'],
                'lastmod' : event['file_date'],
            })
        except Exception as e:
            print("ERROR: {}".format(e))
        

    future = list(filter(lambda x: x['start_date'] >= now, conferences))
    #print(future)
    main_template = env.get_template('index.html')
    with open(root + '/index.html', 'w', encoding="utf-8") as fh:
        fh.write(main_template.render(
            h1          = 'Open Source conferences',
            title       = 'Open Source conferences',
            conferences = future,
            stats       = stats,
        ))
    sitemap.append({
        'url' : '/'
    })

    about_template = env.get_template('about.html')
    with open(root + '/about', 'w', encoding="utf-8") as fh:
        fh.write(about_template.render(
            h1          = 'About Open Source conferences',
            title       = 'About Open Source conferences',
        ))
    sitemap.append({ 'url' : '/about' })


    with open(root + '/conferences', 'w', encoding="utf-8") as fh:
        fh.write(main_template.render(
            h1          = 'Tech related conferences',
            title       = 'Tech related conferences',
            conferences = conferences,
        ))
    sitemap.append({
        'url' : '/conferences'
    })

    cfp = list(filter(lambda x: 'cfp_date' in x and x['cfp_date'] >= now, conferences))
    cfp.sort(key=lambda x: x['cfp_date'])
    #cfp_template = env.get_template('cfp.html')
    with open(root + '/cfp', 'w', encoding="utf-8") as fh:
        fh.write(main_template.render(
            h1          = 'Call for Papers',
            title       = 'Call of Papers',
            conferences = cfp,
        ))
    sitemap.append({
        'url' : '/cfp'
    })

    with open(root + '/404.html', 'w', encoding="utf-8") as fh:
        template = env.get_template('404.html')
        fh.write(template.render(
            h1          = '404',
            title       = 'Four Oh Four',
        ))

    no_code = list(filter(lambda x: not x.get('code_of_conduct'), conferences))
    code_template = env.get_template('code-of-conduct.html')
    with open(root + '/code-of-conduct', 'w', encoding="utf-8") as fh:
        fh.write(code_template.render(
            h1          = 'Code of Conduct',
            title       = 'Code of Conduct (or lack of it)',
            conferences = list(filter(lambda x: x['start_date'] >= now, no_code)),
            earlier_conferences = list(filter(lambda x: x['start_date'] < now, no_code)),
            stats       = stats,

        ))
    sitemap.append({
        'url' : '/code-of-conduct'
    })

    diversity_tickets = list(filter(lambda x: x.get('diversitytickets'), conferences))
    dt_template = env.get_template('diversity-tickets.html')
    with open(root + '/diversity-tickets', 'w', encoding="utf-8") as fh:
        fh.write(dt_template.render(
            h1          = 'Diversity Tickets',
            title       = 'Diversity Tickets',
            conferences = list(filter(lambda x: x['start_date'] >= now, diversity_tickets)),
            earlier_conferences = list(filter(lambda x: x['start_date'] < now, diversity_tickets)),
            stats       = stats,
        ))
    sitemap.append({
        'url' : '/diversity-tickets'
    })


    save_pages(root, 't', topics, sitemap, main_template, now, 'Open source conferences discussing {}')
    save_pages(root, 'l', countries, sitemap, main_template, now, 'Open source conferences in {}')
    save_pages(root, 'l', cities, sitemap, main_template, now, 'Open source conferences in {}')

    collections_template = env.get_template('topics.html')
    save_collections(root, 't', 'topics', 'Topics', topics, sitemap, collections_template, stats, now)
    save_collections(root, 'l', 'countries', 'Countries', countries, sitemap, collections_template, stats, now)
    save_collections(root, 'l', 'cities', 'Cities', cities, sitemap, collections_template, stats, now)

    with open(root + '/sitemap.xml', 'w', encoding="utf-8") as fh:
        fh.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for e in sitemap:
            fh.write('  <url>\n')
            fh.write('    <loc>http://conferences.szabgab.com{}</loc>\n'.format(e['url']))
            date = now
            if 'lastmod' in e:
                date = e['lastmod']
            fh.write('    <lastmod>{}</lastmod>\n'.format(date))
            fh.write('  </url>\n')
        fh.write('</urlset>\n')

def save_collections(root, directory, filename, title, data, sitemap, template, stats, now):
    for d in data.keys():
        data[d]['future'] = len(list(filter(lambda x: x['start_date'] >= now, data[d]['events'])))
        data[d]['total'] =  len(data[d]['events'])
    with open(root + '/' + filename, 'w', encoding="utf-8") as fh:
        fh.write(template.render(
            h1          = title,
            title       = title,
            data        = data,
            directory   = directory,
            stats       = stats,
        ))
    sitemap.append({
        'url' : '/' + filename
    })

def save_pages(root, directory, data, sitemap, main_template, now, title):
    my_dir =  root + '/' + directory + '/'
    if not os.path.exists(my_dir):
        os.mkdir(my_dir)
    for d in data.keys():
        conferences = sorted(data[d]['events'], key=lambda x: x['start_date'])
        #print("'{}'".format(d))
        #print(my_dir + d)
        with open(my_dir + d, 'w', encoding="utf-8") as fh:
            fh.write(main_template.render(
                h1          = title.format(data[d]['name']),
                title       = title.format(data[d]['name']),
                conferences = filter(lambda x: x['start_date'] >= now, conferences),
                earlier_conferences = filter(lambda x: x['start_date'] < now, conferences),
            ))
        sitemap.append({
            'url' : '/' + directory + '/' + d
        })

def preprocess_events(now, conferences, videos):
    countries = {}
    cities = {}
    stats = {
        'total' : len(conferences),
        'future': len(list(filter(lambda x: x['start_date'] >= now, conferences))),
        'cfp'   : len(list(filter(lambda x: x.get('cfp_date', '') >= now, conferences))),
        'has_coc' : 0,
        'has_coc_future' : 0,
        'has_a11y' : 0,
        'has_a11y_future' : 0,
        'has_diversity_tickets' : 0,
        'has_diversity_tickets_future' : 0,
    }

    ev = {}
    for v in videos:
        if v['event'] not in ev:
            ev[ v['event'] ] = []
        ev[ v['event'] ].append(v)

    for event in conferences:
        if event['nickname'] in ev:
            event['videos'] = ev[ event['nickname'] ]

        if not 'country' in event or not event['country']:
            exit('Country is missing from {}'.format(event))
        country_name = event['country']
        country_page = re.sub(r'\s+', '-', country_name.lower())
        event['country_page'] = country_page
        if country_page not in countries:
            countries[country_page] = {
                'name' : country_name,
                'events' : []
            }
        countries[country_page]['events'].append(event)

        if 'city' not in event or not event['city']:
            exit("City is missing from {}".format(event))

        city_name = '{}, {}'.format(event['city'], event['country'])
        city_page = topic2path('{} {}'.format(event['city'], event['country']))

        # In some countris we require state:
        if event['country'] in ['Australia', 'Brasil', 'India', 'USA']:
            if 'state' not in event or not event['state']:
                exit('State is missing from {}'.format(event))
            city_name = '{}, {}, {}'.format(event['city'], event['state'], event['country'])
            city_page = topic2path('{} {} {}'.format(event['city'], event['state'], event['country']))
        if city_page not in cities:
            cities[city_page] = {
                'name' : city_name,
                'events' : []
            }
        cities[city_page]['events'].append(event)

        if event.get('diversitytickets'):
            stats['has_diversity_tickets'] += 1
            if event['start_date'] >= now:
                stats['has_diversity_tickets_future'] += 1
        if event.get('code_of_conduct'):
            stats['has_coc'] += 1
            if event['start_date'] >= now:
                stats['has_coc_future'] += 1
        if event.get('accessibility'):
            stats['has_a11y']
            if event['start_date'] >= now:
                stats['has_a11y_future'] += 1

        if 'cfp_date' in event and event['cfp_date'] >= now:
            tweet_cfp = 'The CfP of {} ends on {} see {} via http://conferences.szabgab.com/'.format(event['name'], event['cfp_date'], event['url'])
            if event['twitter']:
                tweet_cfp += ' @' + event['twitter']
            for t in event['topics']:
                tweet_cfp += ' #' + t['name']
            event['tweet_cfp'] = urllib.parse.quote(tweet_cfp)

        tweet_me = event['name']
        tweet_me += ' on ' + event['start_date']
        tweet_me += ' in ' + event['city']
        if 'state' in event:
            tweet_me += ', ' + event['state']
        tweet_me += ' ' + event['country']
        if event['twitter']:
            tweet_me += ' @' + event['twitter']
        tweet_me += " " + event['url']
        for t in event['topics']:
            tweet_me += ' #' + t['name']
        #tweet_me += ' via @szabgab'
        tweet_me += ' via http://conferences.szabgab.com/'

        event['tweet_me'] = urllib.parse.quote(tweet_me)

    stats['coc_future_perc']  = int(100 * stats['has_coc_future'] / stats['future'])
    stats['diversity_tickets_future_perc']  = int(100 * stats['has_diversity_tickets_future'] / stats['future'])
    stats['a11y_future_perc'] = int(100 * stats['has_a11y_future'] / stats['future'])

    return stats, countries, cities


def topic2path(tag):
    t = tag.lower()
    t = re.sub(r'í', 'i', t)
    t = re.sub(r'ó', 'o', t)
    t = re.sub(r'ã', 'a', t)
    t = re.sub(r'[\W_]+', '-', t)
    return t

main()

# vim: expandtab
