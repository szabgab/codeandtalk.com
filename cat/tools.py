from datetime import datetime
import json

def read_json(filename):
    # catapp.logger.debug("Reading '{}'".format(filename))
    try:
        with open(filename) as fh:
            data = json.loads(fh.read())
    except Exception as e:
        # catapp.logger.error("Reading '{}' {}".format(filename, e))
        data = {}
        pass
    return data

def in_sec(length):
    parts = [int(x) for x in length.split(':')]
    sec = 0
    #print(parts)
    while len(parts) > 0:
        sec *= 60
        sec += parts.pop(0)
    return sec

def future(cat):
    now = datetime.now().strftime('%Y-%m-%d')
    return sorted(
        list(filter(lambda e: e['event_start'] >= now, cat["events"].values())),
        key = lambda e: e['event_start'])

# vim: expandtab
