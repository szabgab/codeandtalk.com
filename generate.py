from datetime import datetime
import glob
import json
import os
import sys
import re
import shutil
import urllib
from jinja2 import Environment, PackageLoader

if sys.version_info.major < 3:
    exit("This code requires Python 3.\nThis is {}".format(sys.version))

def main():
    conferences, topics = read_files()
    #print(conferences)
    generate_pages(conferences, topics)

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

def generate_pages(conferences, topics):
    root = 'html'
    if os.path.exists(root):
        shutil.rmtree(root)
    shutil.copytree('src', root)

    sitemap = []

    now = datetime.now().strftime('%Y-%m-%d')
    #print(now)


    stats, countries, cities = preprocess_events(now, conferences)

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
                'url' : '/e/' + event['nickname']
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


    no_code = list(filter(lambda x: not x.get('code_of_conduct'), conferences))
    code_template = env.get_template('code-of-conduct.html')
    with open(root + '/code-of-conduct', 'w', encoding="utf-8") as fh:
        fh.write(code_template.render(
            h1          = 'Code of Conduct',
            title       = 'Code of Conduct (or lack of it)',
            conferences = no_code,
        ))
    sitemap.append({
        'url' : '/code-of-conduct'
    })

    save_pages(root, 't', topics, sitemap, main_template, now, 'Open source conferences discussing {}')
    save_pages(root, 'l', countries, sitemap, main_template, now, 'Open source conferences in {}')
    save_pages(root, 'l', cities, sitemap, main_template, now, 'Open source conferences in {}')

    collections_template = env.get_template('topics.html')
    save_collections(root, 't', 'topics', 'Topics', topics, sitemap, collections_template)
    save_collections(root, 'l', 'countries', 'Countries', countries, sitemap, collections_template)
    save_collections(root, 'l', 'cities', 'Cities', cities, sitemap, collections_template)

    with open(root + '/sitemap.xml', 'w', encoding="utf-8") as fh:
        fh.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for e in sitemap:
            fh.write('  <url>\n')
            fh.write('    <loc>http://conferences.szabgab.com{}</loc>\n'.format(e['url']))
            fh.write('    <lastmod>{}</lastmod>\n'.format(now))
            fh.write('  </url>\n')
        fh.write('</urlset>\n')

def save_collections(root, directory, filename, title, data, sitemap, template):
    with open(root + '/' + filename, 'w', encoding="utf-8") as fh:
        fh.write(template.render(
            h1          = title,
            title       = title,
            data        = data,
            directory   = directory,
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

def preprocess_events(now, conferences):
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
    }
    for event in conferences:
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
