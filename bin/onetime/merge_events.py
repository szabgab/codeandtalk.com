import json
import glob
import re

# make sure each event has an entry in the series file

with open('data/series.json') as fh:
    series = json.load(fh)

for filename in glob.glob('data/events/*.json'):
    #print(filename)
    with open(filename) as fh:
        data = json.load(fh)

    m = re.search(r'([^/]*)-\d\d\d\d.json$', filename)
    if not m:
        m = re.search(r'([^/]*)-\d\d\d\d-\d\d.json$', filename)
    if not m:
        raise Exception("Invalid file format '{}'".format(filename))
    name = m.group(1) 
    if name in series:
       if series[name]['name'] != data['name']:
           raise Exception("Names differ for {} in event: '{}' in series: '{}'".format(filename, data['name'], series[name]['name']))
    else:
        series[name] = {
           'name' : data['name']
        }
    del data['name']

    if 'events' not in series[name]:
        series[name]['events'] = []

    if 'twitter' in data:
        if data['twitter'] == '':
            del data['twitter']
        else:
            twitter = data.pop('twitter').lower()
            if 'twitter' in series[name]:
                if series[name]['twitter'] != twitter:
                    raise Exception("Twitter differs for {} in event: '{}' in series: '{}'".format(filename, twitter, series[name]['twitter']))
            else:
                series[name]['twitter'] = twitter

    if 'facebook' in data:
        if data['facebook'] == '':
            del data['facebook']
        else:
            if name in ['foss4g', 'puppetconf', 'ubucon-europe']:
                continue
            facebook = data.pop('facebook')
            if not 'facebook' in series[name]:
                series[name]['facebook'] = facebook
            if series[name]['facebook'] != facebook:
               raise Exception("Facebook differs for series {} of {} in event: '{}' in series: '{}'".format(name, filename, facebook, series[name]['facebook']))
    

    series[name]['events'].append(data)


for s in series:   
    filename = 'data/e/' + s + '.json'
    #print(filename)
    with open(filename, 'w') as fh:
        json.dump(series[s], fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

