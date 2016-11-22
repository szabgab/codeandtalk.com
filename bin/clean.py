import json
import glob

# format the json files

for filename in glob.glob("data/*.json"):
	with open(filename) as fh:
		data = json.load(fh)
	with open(filename, 'w') as fh:
		json.dump(data, fh, sort_keys=True, indent=4, separators=(',', ': '))

