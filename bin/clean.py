#!/usr/bin/env python3
import json
import glob

# format the json files

for filename in glob.glob("data/*.json") + glob.glob("data/podcasts/*.json"):
	with open(filename) as fh:
		data = json.load(fh)
	with open(filename, 'w') as fh:
		json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '))

for filename in glob.glob("data/videos/*/*.json"):
	with open(filename) as fh:
		data = json.load(fh)
	if data['speakers']:
		#print(filename)
		with open(filename, 'w') as fh:
			json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '))

