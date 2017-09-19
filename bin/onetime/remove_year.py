import json
import glob
import re

# remove the year from the end of the even name as we can add it automatically during display
# also we won't want it after we merge the event series

for filename in glob.glob('data/events/*.json'):
    #print(filename)
    with open(filename) as fh:
        data = json.load(fh)
    #print(data['name'])
    data['name'] = re.sub(r'(\s*-)?\s*\d\d\d\d\s*$', '', data['name'])
    #print(data['name'])
    with open(filename, 'w') as fh:
        json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

