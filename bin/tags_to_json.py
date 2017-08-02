import json
import csv
import sys
import os
import re

# onetime script to convert the data/tags.csv to data/tags.json

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

def read_chars():
    tr = {}
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, 'cat', 'chars.csv'), encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter=',') 
        for row in rd:
            tr[row[0]] = row[1]
    return tr

tr = read_chars()
tags = {}
with open(os.path.join('data', 'tags.csv'), encoding="utf-8") as fh:
    rd = csv.DictReader(fh, delimiter=';')
    for row in rd:
        path = topic2path(row['name'])
        if row['description'] == None:
            row['description'] = ''
        tags[ path ] = {
            'name'        : row['name'],
            'url'         : row['url'],
            'description' : row['description'],
        }

with open(os.path.join('data', 'tags.json'), 'w', encoding="utf-8") as fh:
    json.dump(tags, fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

