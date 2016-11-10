from datetime import datetime
import os
import json
import scrapy
import re

# scrapy runspider --nolog fetch_floss_weekly.py -a start=23

class FlossWeeklySpider(scrapy.Spider):
    name = "floss-weekly"
    # read data/floss-weekly.json to get the list of already parsed 
    filename = 'data/floss-weekly.json'
    with open(filename) as fh:
        episodes = json.load(fh)


    def start_requests(self):
        #print(self)
        start = int(getattr(self, 'start', 1))
        end = int(getattr(self, 'end', start+1))
        
        #print(start, end)
        collected = [x['ep'] for x in FlossWeeklySpider.episodes]
        for ep in [str(x) for x in range(start, end)]:
            if ep not in collected:
                url = 'https://twit.tv/shows/floss-weekly/episodes/' + ep
                yield scrapy.Request(url, self.parse)


    def parse(self, response):
        data = {
            'keywords' : [],
            'guests'   : {},
            'hosts'    : {},
        }
        #print(response)
        data['permalink'] = response.url
        full_title = response.css('title::text').extract_first()
        print(full_title)
        published  = response.css('p.air-date::text').extract_first()
        print(published) # Apr 25th 2012
        parsable = re.sub(r'\A(\w+)\s+(\d+)\w+\s+(\d+)\Z', r'\1 \2 \3', published)
        print(parsable)
        dt = datetime.strptime(parsable, '%b %d %Y')  # Apr 25 2012
        print(dt)
        data['date'] = dt.strftime('%Y-%m-%d')
        m = re.search(r'FLOSS Weekly (\d+)\s+(.*?)\s+\| TWiT', full_title)
        #m = re.search(r'FLOSS Weekly (\d+)\s+(.*)', full_title)

        #hosts_div = response.css('div.hosts')
        #host_names = hosts_div.css('a::text')
        host_names = response.css('div.hosts').css('a::text').extract()
        for name in host_names:
            handle = re.sub(r'\s+', '-', name.lower())
            if re.search('^[\w-]+$', handle):
                person_file = 'data/people/' + handle + '.txt'
                if not os.path.exists(person_file):
                    print('Creating {}'.format(person_file))
                    with open(person_file, 'w') as fh:
                        fh.write('name: {}\n'.format(name))
                #data['hosts'].append(handle)
                data['hosts'][handle] = {}
            else:
                print("WARN Invalid character in name of {}".format(h))
        #print(host_names)
        if m:
            data['ep'] = m.group(1)
            data['title'] = m.group(2)
        print(data)
        FlossWeeklySpider.episodes.append(data)
        FlossWeeklySpider.episodes.sort(key=lambda x: int(x['ep']) )
        with open(FlossWeeklySpider.filename, 'w') as fh:
            json.dump(FlossWeeklySpider.episodes, fh, sort_keys=True, indent=4, separators=(',', ': '))


# vim: expandtab
