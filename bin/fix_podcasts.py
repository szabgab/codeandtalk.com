import json
import os
import glob

# one-time script refactoring the format of the podcast files

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

path = os.path.join(root, 'data', 'podcasts')

for file in glob.glob(path + "/*.json"):
    print(file)
#    continue
    with open(file) as fh:
        data = json.load(fh)
    for episode in data:
        for field in ('hosts', 'guests'):
            if field in episode:
                episode[field] = list(episode[field].keys())
    with open(file, 'w') as fh:
        json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '))
