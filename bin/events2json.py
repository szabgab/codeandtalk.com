import json
import glob
import re
import os

# one time script converting txt files to json files

for event_file in glob.glob("data/events/*.txt"):
    #print(event_file)
    json_file = event_file[:-3] + 'json'
    #print(json_file)
    event = {}
    with open(event_file) as fh:
        for line in fh:
            line = re.sub(r'\s+$', '', line)
            if line == '':
                continue
            m = re.search(r'^(\w+)\s*:\s*(.*)$', line)
            if m:
	             event[m.group(1)] = m.group(2)
            else:
                print("Invalid row '{}' in file {}".format(line, event_file))
    with open(json_file, 'w') as fh:
        json.dump(event, fh, sort_keys=True, indent=4, separators=(',', ': '))
#    os.system("git rm " + event_file)
#    os.system("git add " + json_file)
