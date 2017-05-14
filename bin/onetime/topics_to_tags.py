import json
import glob
import re
import sys
import os
import csv

def read_chars():
    tr = {}
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, 'cat', 'chars.csv')) as fh:
        rd = csv.reader(fh, delimiter=',')
        for row in rd:
            tr[row[0]] = row[1]
    return tr
tr = read_chars()

# one time script updating the event files  topics to tags
def main():

    for json_file in glob.glob("data/events/*.json"):
        with open(json_file) as fh:
            event = json.load(fh)
        if 'topics' in event:
            topics = event.pop('topics')
            tags = []
            if topics != '':
                for t in re.split(r'\s*,\s*', topics.lower()):
                    p = topic2path(t)
                    tags.append(p)
            event['tags'] = tags

            with open(json_file, 'w') as fh:
                json.dump(event, fh, sort_keys=True, indent=4, separators=(',', ': '))


# copied from code.py
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



main()