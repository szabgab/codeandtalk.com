import argparse
from datetime import datetime
import glob
import json
import os
import sys
import re
import shutil
import urllib
from jinja2 import Environment, PackageLoader

from xcast.people import read_people, read_tags, read_videos, read_events, read_episodes

if sys.version_info.major < 3:
    exit("This code requires Python 3.\nThis is {}".format(sys.version))


def process_conferences():
    conferences, topics = read_events()
    #print(conferences)
    people = read_people('data/people')
    videos = read_videos(topics) # bad bad that topics will be updated!
    #print(people)

    events = {}
    for e in conferences:
        events[ e['nickname'] ] = e
    for v in videos:
        v['twitter_description'] = html2txt(v['description'])
        v['event_name'] = events[ v['event'] ]['name']
        speakers = {}
        for s in v['speakers']:
            if s in people:
                speakers[s] = people[s]
            else:
                print("WARN: Missing people file for '{}'".format(s))
        v['speakers'] = speakers

        tweet_video = '{} http://conferences.szabgab.com/v/{}/{}'.format(v['title'], v['event'], v['filename'])
        tw_id = events[ v['event'] ].get('twitter', '')
        if tw_id:
            tweet_video += ' presented @' + tw_id
        #print(v['speakers'])
        #exit()
        if v['speakers']:
            for s in v['speakers']:
                tw_id = v['speakers'][s]['info'].get('twitter', '')
                if tw_id:
                    tweet_video += ' by @' + tw_id
        if 'tags' in v:
            for t in v['tags']:
                if not re.search(r'-', t['link']) and len(t['link']) < 10:
                    tweet_video += ' #' + t['link']
        v['tweet_video'] = urllib.parse.quote(tweet_video)


        #print(speakers)
        #exit()
            

    generate_pages(conferences, topics, videos, people)


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
            videos      = (directory == 't'),
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
                conferences = list(filter(lambda x: x['start_date'] >= now, conferences)),
                earlier_conferences = list(filter(lambda x: x['start_date'] < now, conferences)),
                videos      = data[d].get('videos'),
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

        city_page = event['city_page']
        if city_page not in cities:
            cities[city_page] = {
                'name' : event['city_name'],
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

def html2txt(html):
    #text = re.sub(r'<a\s+href="[^"]+">([^<]+)</a>', '$1', html)
    text = re.sub(r'</?[^>]+>', '', html)
    return text

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--html', help = 'Generate HTML', action='store_true')
    parser.add_argument('--check', help = 'Check the RSS feed', action='store_true')
    parser.add_argument('--source', help = 'Check the RSS feed of given source')
    args = parser.parse_args()

    with open('data/sources.json', encoding="utf-8") as fh:
        sources = json.load(fh)
    
    if args.source:
        check_rss_feed()
    elif args.check:
        check_rss()
    elif args.html:

        root = 'html'
        if os.path.exists(root):
            shutil.rmtree(root)
        shutil.copytree('src', root)

        process_conferences()

        episodes = read_episodes(sources)
        people = read_people('data/people')
        tags = read_tags()

        for e in episodes:
            #print(e)
            #exit()
            if 'tags' in e:
                for tag in e['tags']:
                    path = tag['link']
                    if path not in tags:
                        # TODO report tag missing from the tags.csv file
                        tags[path] = {}
                        tags[path]['tag'] = tag['text']
                        tags[path]['episodes'] = []
                    tags[path]['episodes'].append(e)

            if 'guests' in e:
                for g in e['guests'].keys():
                    if g not in people:
                        exit("ERROR: '{}' is not in the list of people".format(g))
                    people[g]['episodes'].append(e)
            if 'hosts' in e:
                for h in e['hosts'].keys():
                    if h not in people:
                        exit("ERROR: '{}' is not in the list of people".format(h))
                    people[h]['hosting'].append(e)
        generate_podcast_pages(sources, people, tags, episodes)
    else:
        parser.print_help()

def generate_podcast_pages(sources, people, tags, episodes):
    env = Environment(loader=PackageLoader('conf', 'templates'))

    search = {}

    for e in episodes:
        search[ e['title'] + ' (ext)' ] = e['permalink']

    person_template = env.get_template('person.html')
    if not os.path.exists('html/p/'):
        os.mkdir('html/p/')
    for p in people.keys():
        people[p]['episodes'].sort(key=lambda x : x['date'], reverse=True)
        people[p]['hosting'].sort(key=lambda x : x['date'], reverse=True)
        if 'name' not in people[p]['info']:
            exit("ERROR: file {} does not have a 'name' field".format(p))
        name = people[p]['info']['name']
        path = '/p/' + p
        search[name] = path

        with open('html' + path, 'w', encoding="utf-8") as fh:
            fh.write(person_template.render(
                id     = p,
                person = people[p],
                h1     = people[p]['info']['name'],
                title  = 'Podcasts of and interviews with {}'.format(people[p]['info']['name']),
            ))

    source_template = env.get_template('podcast.html')
    if not os.path.exists('html/s/'):
        os.mkdir('html/s/')
    for s in sources:
        search[ s['title'] ] = '/s/' + s['name'];
        try:
            with open('html/s/' + s['name'], 'w', encoding="utf-8") as fh:
                fh.write(source_template.render(
                    podcast = s,
                    h1     = s['title'],
                    title  = s['title'],
                ))
        except Exception as e:
            print("ERROR: {}".format(e))
            

    tag_template = env.get_template('tag.html')
    if not os.path.exists('html/t/'):
        os.mkdir('html/t/')
    for t in tags:
        search[ tags[t]['tag'] ] = '/t/' + t;
        with open('html/t/' + t, 'w', encoding="utf-8") as fh:
            #tags[t]['path'] = t
            fh.write(tag_template.render(
                tag   = tags[t],
                h1    = tags[t]['tag'],
                title = tags[t]['tag'],
                #title = 'Podcasts and discussions about {}'.format(tags[t]['tag'])
            ))


    stats = {
        'sources'  : len(sources),
        'people'   : len(people),
        'episodes' : sum(len(x['episodes']) for x in sources)
    }

    #main_template = env.get_template('index.html')
    #with open('html/index.html', 'w', encoding="utf-8") as fh:
    #    fh.write(main_template.render(
    #        h1      = 'xCast - Tech related podcast and presentations',
    #        title   = 'xCast - Tech related podcast and presentations',
    #        stats   = stats,
    #        tags    = tags,
    #        sources = sources,
    #        people = people,
    #        people_ids = sorted(people.keys()),
    #    ))

    with open('html/people', 'w', encoding="utf-8") as fh:
        fh.write(env.get_template('people.html').render(
            h1      = 'List of people',
            title   = 'List of people',
            stats   = stats,
            tags    = tags,
            people = people,
            people_ids = sorted(people.keys()),
        ))
    with open('html/podcasts', 'w', encoding="utf-8") as fh:
        fh.write(env.get_template('podcasts.html').render(
            h1      = 'List of podcasts',
            title   = 'List of podcasts',
            stats   = stats,
            tags    = tags,
            podcasts = sorted(sources, key=lambda x: x['title']),
            people = people,
            people_ids = sorted(people.keys()),
         ))
    with open('html/tags', 'w', encoding="utf-8") as fh:
        fh.write(env.get_template('tags.html').render(
            h1      = 'Tags',
            title   = 'Tags',
            stats   = stats,
            tags    = tags,
            people = people,
            people_ids = sorted(people.keys()),
        ))
    with open('html/search.json', 'w', encoding="utf-8") as fh:
        json.dump(search, fh)

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
