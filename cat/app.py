from flask import Flask, render_template, redirect, abort, request, url_for, Response, jsonify
import copy
from datetime import datetime, timedelta
import os
import json
import re
import urllib
import sys

root = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, root)
from cat import tools
from cat.tools import read_json

catapp = Flask(__name__)
catapp.config['PROPAGATE_EXCEPTIONS'] = True

@catapp.route("/")
def main():
    cat = read_json(root + '/html/cat.json')
    return render_template('index.html',
        h1          = 'Presentations from tech events worth watching',
        title       = 'Conferences, Videos, Podcasts, and People',
        stats       = cat['stats'],
    )

@catapp.route("/featured-by-date")
@catapp.route("/featured")
def featured():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')
    featured_by_date = {}
    featured_by_blaster = {}

    for video in cat['videos']:
        featured = video.get('featured')
        blasters = video.get('blasters', [])
        if featured:
            class_name = ''
            if video['featured'] == now:
                class_name = 'today_feature'
            elif video['featured'] > now:
                class_name = 'future_feature'
            video['class_name'] = class_name
            if featured not in featured_by_date:
                featured_by_date[featured] = []
            featured_by_date[featured].append(video)

            for b in blasters:
                if b not in featured_by_blaster:
                    featured_by_blaster[ b ] = []
                featured_by_blaster[b].append(video)

    if request.path == '/featured':
        return render_template('featured.html',
            h1     = 'Featured Videos',
            title  = 'Featured Videos',
            featured_by_blaster = featured_by_blaster,
        )
    elif request.path == '/featured-by-date':
        return render_template('featured-by-date.html',
            h1     = 'Featured Videos',
            title  = 'Featured Videos',
            featured_by_date    = featured_by_date,
        )
    else:
        return 'Oups'

@catapp.route("/about")
def about(filename = None):
    cat = read_json(root + '/html/cat.json')
    return render_template('about.html',
        h1          = 'About Code And Talk',
        title       = 'About Code And Talk',
        stats       = cat['stats'],
    )

@catapp.route("/contribute")
def contribute(filename = None):
    cat = read_json(root + '/html/cat.json')
    return render_template('contribute.html',
        h1          = 'Contribute to Code And Talk',
        title       = 'Contribute to Code And Talk',
        stats       = cat['stats'],
    )

@catapp.route("/conferences")
def conferences():
    cat = read_json(root + '/html/cat.json')
    return render_template('list.html',
        h1          = 'Open Source conferences',
        title       = 'Open Source conferences',
        conferences = tools.future(cat),
        stats       = cat['stats'],
        cal         = 'all.ics',
    )
@catapp.route("/all-conferences")
def all_conferences():
    cat = read_json(root + '/html/cat.json')
    events = []
    for nick in cat['events'].keys():
        event = copy.deepcopy(cat['events'][nick])
        if 'youtube' in event and event['youtube'] == '-':
            event['youtube'] = None
        events.append(event)

    return render_template('list.html',
        h1          = 'All the Tech related conferences',
        title       = 'All the Tech related conferences',
        conferences = events,
    )

@catapp.route("/cfp")
def cfp_conferences():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')
    cfp = sorted(list(filter(lambda e: 'cfp_end' in e and e['cfp_end'] >= now, cat["events"].values())), key = lambda e: e['event_start'])
    return render_template('list.html',
        h1          = 'Call for Papers',
        title       = 'Call for Papers',
        conferences = cfp,
    )

@catapp.route("/code-of-conduct")
def code_of_conduct():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')

    no_code = list(filter(lambda e: not e.get('code_of_conduct'), cat['events'].values()))
    return render_template('code-of-conduct.html',
        h1          = 'Code of Conduct',
        title       = 'Code of Conduct (or lack of it)',
        conferences = list(filter(lambda x: x['event_start'] >= now, no_code)),
        earlier_conferences = list(filter(lambda x: x['event_start'] < now, no_code)),
        stats       = cat['stats'],
    )

@catapp.route("/diversity-tickets")
def diversity_tickets():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')

    diversity_tickets = list(filter(lambda e: e.get('diversitytickets'), cat['events'].values()))
    return render_template('diversity-tickets.html',
        h1          = 'Diversity Tickets',
        title       = 'Diversity Tickets',
        conferences = list(filter(lambda e: e['event_start'] >= now, diversity_tickets)),
        earlier_conferences = list(filter(lambda e: e['event_start'] < now, diversity_tickets)),
        stats       = cat['stats'],
    )


@catapp.route("/blasters")
def blasters():
    cat = read_json(root + '/html/cat.json')
    return render_template('blasters.html',
        h1           = 'Blasters - get notified about new videos',
        title        = 'Blasters',
        all_blasters = cat['blasters'],
    )


@catapp.route("/videos")
def videos():
    term = _term()
    mindate = _term('mindate')
    maxdate = _term('maxdate')
    mintime = _term('mintime')
    maxtime = _term('maxtime')
    if mintime:
        min_sec = tools.in_sec(mintime)
    if maxtime:
        max_sec = tools.in_sec(maxtime)

    cat = read_json(root + '/html/cat.json')
    results = []
    if term != '' or mindate or maxdate or mintime or maxtime:
        for v in cat['videos']:
            if mindate and v['recorded'] < mindate:
                continue
            if maxdate and v['recorded'] > maxdate:
                continue
            if mintime and v['l'] < min_sec:
                continue
            if maxtime and v['l'] > max_sec:
                continue
            if term != '':
                if term in v['title'].lower():
                    results.append(v)
                    continue
                if term in v['short_description'].lower():
                    results.append(v)
                    continue
                if 'tags' in v:
                    tags = [x['link'] for x in v['tags']]
                    if term in tags:
                        results.append(v)
                        continue
            else:
                results.append(v)
                continue

    return render_template('videos.html',
        title            = 'Tech videos worth watching', 
        h1               = 'Videos',
        number_of_videos = len(cat['videos']),
        term             = term,
        mindate          = mindate,
        maxdate          = maxdate,
        mintime          = mintime,
        maxtime          = maxtime,
        videos           = results,
        people           = cat['people'],
        events           = cat['events'],
    )


@catapp.route("/people")
def people():
    term = _term()
    cat = read_json(root + '/html/cat.json')
    ppl = cat['people']
    result = {}
    if term != '':
        for nickname in ppl.keys():
            if re.search(term, ppl[nickname]['info']['name'].lower()):
                catapp.logger.debug("People: '{}'".format(nickname))
                result[nickname] = ppl[nickname]
            elif re.search(term, ppl[nickname]['info'].get('location', '').lower()):
                result[nickname] = ppl[nickname]
            elif term in ppl[nickname]['info'].get('topics', []):
                result[nickname] = ppl[nickname]
            #elif 'tags' in ppl[nickname] and term in ppl[nickname]['tags']:
            #    result[nickname] = ppl[nickname]

    return render_template('people.html',
        title            = 'People who talk at conferences or in podcasts', 
        h1               = 'People who talk',
        number_of_people = len(ppl.keys()),
        term             = term,
        people           = result,
        people_ids       = sorted(result.keys()),
    )

@catapp.route("/series")
def series():
    cat = read_json(root + '/html/cat.json')
    return render_template('series.html',
        h1     = 'Event Series',
        title  = 'Event Series',
        series = cat['series'],
    )

@catapp.route("/topics")
@catapp.route("/countries")
@catapp.route("/cities")
def serve_collections():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')
    directories = {
        '/topics'    : 't',
        '/countries' : 'l',
        '/cities'    : 'l',
    }
    titles = {
        '/topics'    : 'Topics',
        '/countries' : 'Countries',
        '/cities'    : 'Cities',
    }
    directory = directories[request.path]
    title     = titles[request.path]

    if request.path == '/cities':
        data = cat['stats']['cities']

    if request.path == '/countries':
        data = cat['stats']['countries']

    if request.path == '/topics':
        data = cat['tags']

    return render_template('topics.html',
            h1          = title,
            title       = title,
            data        = data,
            directory   = directory,
            stats       = cat['stats'],
            videos      = (directory == 't'),
            episodes    = (directory == 't'),
        )


@catapp.route("/v/<event>/<filename>")
def show_video(event = None, filename = None):
    cat = read_json(root + '/html/cat.json')
    for vid in cat['videos']:
        if vid['event'] == event and vid['filename'] == filename:
            video = vid
            break
    else:
        return not_found()

    speakers = []
    speaker_twitters = ''

    for s in video['speakers']:
        p = copy.deepcopy(cat['people'][s])
        p['nickname'] = s
        speakers.append(p)
        tw = p['info'].get('twitter')
        if tw:
            speaker_twitters += ' @' + tw

    return render_template('video.html',
        h1          = video['title'],
        title       = video['title'],
        video       = video,
        blasters    = video.get('blasters'),
        events      = cat['events'],
        speakers    = speakers,
        speaker_twitters = speaker_twitters,
        tweet_video = get_tweet_video(video, speakers, cat['events'][ video['event'] ]),
    )

@catapp.route("/p/<nickname>")
def show_person(nickname = None):
    cat = read_json(root + '/html/cat.json')

    if nickname not in cat['people']:
        return not_found()

    person = copy.deepcopy(cat['people'][nickname])
    person['videos'] = []
    for video in cat['videos']:
        if nickname in video['speakers']:
            person['videos'].append(video)

    podcasts = {
        'guests' : [],
        'hosts'  : [],
    }
    for field in ['guests', 'hosts']:
        for podcast in cat['podcasts']:
            for episode in podcast['episodes']:
                if field in episode:
                    if nickname in episode[field]:
                        podcasts[field].append(episode)

#        for field in ['episodes', 'hosting']:
#            if field not in self.people[p]:
#                self.people[p][field] = []
#            self.people[p][field].sort(key=lambda x : x['date'], reverse=True)
    return render_template('person.html',
        h1          = person['info']['name'],
        title       = 'Presentations and podcasts by ' + person['info']['name'],
        person      = person,
        events      = cat['events'],
        id          = nickname,
        podcasts    = podcasts,
    )
    #for r in self.redirects:
    #    with open(self.html + '/p/' + r['from'], 'w') as fh:
    #        fh.write('<meta http-equiv="refresh" content="0; url=https://codeandtalk.com/p/{}" />\n'.format(r['to']))
    #        fh.write('<p><a href="https://codeandtalk.com/p/{}">Moved</a></p>\n'.format(r['to']))


@catapp.route("/cal/all.ics")
@catapp.route("/cal/l/<location>.ics")
@catapp.route("/cal/t/<tag>.ics")
def calendar(location = None, tag = None):
    cat = read_json(root + '/html/cat.json')

    if location:
        name, future, past = events_in_location(cat, location)
        prodid = 'l/{}'.format(location)
    elif tag:
        future, past = events_by_tag(cat, tag)
        prodid = 't/{}'.format(tag)
    else:
        future = tools.future(cat)
        prodid = 'all'

    if not future:
        return not_found()

    cal = _calendar(prodid, future)
    return cal
    #return Response(cal, mimetype="text/calendar")

@catapp.route("/t/<tag>")
def by_tag(tag):
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')

    future, earlier = events_by_tag(cat, tag)

    videos = []
    for video in cat['videos']:
        #if 'tags' in video:
        #    catapp.logger.debug("Video '{}'".format(video['tags']))
        if 'tags' in video and tag in [ t['link'] for t in video['tags'] ]:
            videos.append(video)

    episodes = episodes_by_tag(cat, tag)

    if not future and not earlier and not videos and not episodes:
        return not_found()

    #catapp.logger.debug("Reading '{}'".format(filename))
    title = 'Open source conferences discussing {}'.format(tag)
    return render_template('list.html',
        h1          = title,
        title       = title,
        conferences = future,
        earlier_conferences = earlier,
        videos      = videos,
        events      = cat['events'],
        #episodes    = data[d].get('episodes'),
        cal         = 't/{}.ics'.format(tag),
    )

# event
@catapp.route("/e/<nickname>")
def event(nickname):
    cat = read_json(root + '/html/cat.json')
    if nickname not in cat['events']:
        return not_found()
    event = copy.deepcopy(cat['events'][nickname])
    if 'youtube' in event and event['youtube'] == '-':
        event['youtube'] = None

    diversity = event.get('diversitytickets', None)
    if diversity:
        catapp.logger.debug("Diversity")
        event['diversitytickets_url'] = "https://diversitytickets.org/events/" + diversity
    if 'diversitytickets_url' in event and 'diversitytickets_text' not in event:
        event['diversitytickets_text'] = 'Diversity Tickets'

    people = {}
    videos = []
    for video in cat['videos']:
        if video['event'] == nickname:
            videos.append(video)
        for s in video['speakers']:
            p = copy.deepcopy(cat['people'][s])
            p['nickname'] = s
            people[s] = p
    series = []
    if 'series' in event:
        series = copy.deepcopy(cat['series'][event['series']])
        for e in series['events']:
            e['year'] = e['event_start'][0:4]
    event['year'] = event['event_start'][0:4]

#    return(str(event))
    return render_template('event.html',
        title = event['name'] + ' ' + event['year'],
        h1    = event['name'] + ' ' + event['year'],
        event = event,
        people = people,
        videos = videos,
        series = series,
    )

@catapp.route("/l/<location>")
def location(location):
    cat = read_json(root + '/html/cat.json')

    name, future, past = events_in_location(cat, location)
    if future == None:
        return not_found()
    title = 'Conferences in {}'.format(name.encode('ascii', 'ignore')) # was needed in Python 2

    return render_template('list.html',
        h1          = title,
        title       = title,
        conferences = future,
        earlier_conferences = past,
        cal         = 'l/{}.ics'.format(location),
    )


@catapp.route("/sitemap.xml")
def sitemap():
    cat = read_json(root + '/html/cat.json')
    now = datetime.now().strftime('%Y-%m-%d')

    sitemap = []
    for event in cat['events'].values():
        sitemap.append({
            'url' : '/e/' + event['nickname'],
            'lastmod' : event['file_date'],
        })

    for page in [
        '/',
        '/about',
        '/all-conferences',
        '/blasters',
        '/cfp',
        '/cities',
        '/code-of-conduct',
        '/conferences',
        '/contribute',
        '/countries',
        '/diversity-tickets',
        '/series',
        '/topics',
        '/videos',
        ]:
        sitemap.append({ 'url' : page })
    #sitemap.append({ 'url' : '/featured' })

    # add tags, cities, and countries to sitemap
    for t in cat['tags']:
        sitemap.append({ 'url' : '/t/' + t })
    for c in cat['stats']['cities']:
        sitemap.append({ 'url' : '/l/' + c })
    for c in cat['stats']['countries']:
        sitemap.append({ 'url' : '/l/' + c })
    #for b in blasters:
    #    sitemap.append({ 'url' : '/blaster/' + b['file'] })

    for video in cat['videos']:
        sitemap.append({
            'url' : '/v/' + video['event'] + '/' + video['filename'],
            'lastmod' : video['file_date'],
        })
 
    html = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for e in sitemap:
        #catapp.logger.debug(e)
        html += '  <url>\n'
        html += '    <loc>https://codeandtalk.com{}</loc>\n'.format(e['url'])
        if 'lastmod' in e:
            date = e['lastmod']
        else:
            date = now
        html += '    <lastmod>{}</lastmod>\n'.format(date)
        html += '  </url>\n'
    html += '</urlset>\n'
    return html

@catapp.route("/s/<source>")
def show_episodes(source):
    cat = read_json(root + '/html/cat.json')
    for p in cat['podcasts']:
        if p['name'] == source:
            podcast = copy.deepcopy(p)
            break
    else:
        return not_found()

    for e in podcast['episodes']:
        for field in ('guests', 'hosts'):
            if field in e:
                people = {}
                for person in e[field]:
                    people[person] = cat['people'][person]['info']
            e[field] = people

    return render_template('podcast.html',
        podcast = podcast,
        h1     = podcast['title'],
        title  = podcast['title'],
    )

@catapp.route("/podcasts")
def show_podcasts():
    cat = read_json(root + '/html/cat.json')
    return render_template('podcasts.html',
       h1      = 'List of podcasts',
       title   = 'List of podcasts',
#       stats   = cat['stats'],
#       tags    = cat['tags'],
       podcasts = sorted(cat['podcasts'], key=lambda s: s['title']),
#       people = cat['people'],
#       people_ids = sorted(cat['people'].keys()),
    )

### static page for the time of transition
@catapp.route("/<filename>")
def static_file(filename = None):
    #index.html  redirect

    mime = 'text/html'
    try:
        content = open(root + '/html/' + filename).read()
    except Exception:
        return not_found()

    if filename[-4:] == '.css':
        mime = 'text/css'
    elif filename[-5:] == '.json':
        mime = 'application/javascript'
    elif filename[-3:] == '.js':
        mime = 'application/javascript'
    elif filename[-4:] == '.xml':
        mime = 'text/xml'
    elif filename[-4:] == '.ico':
        mime = 'image/x-icon'
    return Response(content, mimetype=mime)

@catapp.route("/blaster/<nickname>")
def show_blaster(nickname):
    cat = read_json(root + '/html/cat.json')
    for b in cat['blasters']:
        if b['file'] == nickname:
            blaster = b
            break
    else:
        return not_found()

    return render_template('blaster.html',
        h1          = blaster['name'] + ' Blaster',
        title       = blaster['name'] + ' Blaster',
        blaster     = blaster,
    )

@catapp.errorhandler(404)
def not_found(e = None):
    return render_template('404.html',
                       h1='404',
                       title='Four Oh Four',
                       ), 404

@catapp.errorhandler(500)
def crashed(e):
    return "Our Page crashed", 500

###### Helper functions

def _term(field = 'term'):
    value = request.args.get(field, '')
    value = value.lower()
    value = re.sub(r'^\s*(.*?)\s*$', r'\1', value)
    return value

def _calendar(prodid, events):
    dtstamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
    cal = ""
    cal += "BEGIN:VCALENDAR\r\n"
    cal += "PRODID:https://codeandtalk.com/cal/{}.ics\r\n".format(prodid)
    cal += "VERSION:2.0\r\n"
    #PRODID:-//http://XXX//Event
    #METHOD:PUBLISH

    for e in events:
        end = datetime.strptime(e['event_end'], '%Y-%m-%d')
        end = end + timedelta(days = 1)
        event_end = end.strftime('%Y%m%d')

        cal += "BEGIN:VEVENT\r\n"
        cal += "DTSTAMP:{}\r\n".format(dtstamp)
        cal += "DTSTART;VALUE=DATE:{}\r\n".format(re.sub(r'-', '', e['event_start']))
        cal += "DTEND;VALUE=DATE:{}\r\n".format(event_end)
        uid = re.sub(r'\W+', '-', e['website'])
        uid = re.sub(r'\W+$', '', uid)
        cal += "UID:{}\r\n".format(uid)
        cal += "SUMMARY:{}\r\n".format(e['name'].encode('ascii', 'ignore')) # was needed in Python 2
        cal += "DESCRIPTION:{}\r\n".format(e['website'])
        try:
            location = e['city']
            if e['state']:
                location += ", " + e['state']
            location += ", " + e['country']
            cal += "LOCATION:{}\r\n".format(location)
        except Exception:
            pass
            # hide Unicode error from beyondtellerrand-2017
        cal += "END:VEVENT\r\n"

    cal += "END:VCALENDAR\r\n"
    return cal

def episodes_by_tag(cat, tag):
    episodes = []
    for podcast in cat['podcasts']:
        for episode in podcast['episodes']:
            if 'tags' in episode:
                for t in episode['tags']:
                    if t['link'] == tag:
                        episodes.append(episode)
    return episodes

def events_by_tag(cat, tag):
    now = datetime.now().strftime('%Y-%m-%d')
    future = []
    earlier = []
    for event in cat['events'].values():
        if tag in [ t['path'] for t in event['topics'] ]:
            if event['event_start'] > now:
                future.append(event)
            else:
                earlier.append(event)
    if not future and not earlier:
        return None, None
    return future, earlier

def events_in_location(cat, location):
    now = datetime.now().strftime('%Y-%m-%d')
    if location in cat['stats']['countries']:
        name = cat['stats']['countries'][location]['name']
        page = 'country_page'
    elif location in cat['stats']['cities']:
        name = cat['stats']['cities'][location]['name']
        page = 'city_page'
    else:
        return None, None, None

    future = []
    past = []
    for e in sorted(cat['events'].values(), key=lambda e: e['event_start']):
        if e[page] == location:
            if e['event_start'] >= now:
                future.append(e)
            else:
                past.append(e)
    return name, future, past

def get_tweet_video(video, speakers, event):
    title = video['title'].encode('ascii', 'ignore') # was needed in Python 2
    tweet_video = '{} https://codeandtalk.com/v/{}/{}'.format(title, video['event'], video['filename'])
    tw_id = event.get('twitter', '')
    if tw_id:
        tweet_video += ' presented @' + tw_id
    #print(v['speakers'])
    #exit()
    if video['speakers']:
        for s in speakers:
            tw_id = s['info'].get('twitter', '')
            if tw_id:
                tweet_video += ' by @' + tw_id

    if 'tags' in video:
        for t in video['tags']:
            p = t['link']
            if not re.search(r'-', t['link']) and len(t['link']) < 20:
                tweet_video += ' #' + t['link']
    if sys.version_info.major < 3:
        return urllib.quote(tweet_video)
    else:
        return urllib.parse.quote(tweet_video)


# vim: expandtab
