import json
import glob
import re


# one time script updating the event files  splitting up the languages field, renaming url to wwebsite

def main():
    for json_file in glob.glob("data/events/*.json"):
        with open(json_file) as fh:
            event = json.load(fh)
        event['languages'] = re.split(r'\s*,\s*', event['languages'])
        event['website'] = event.pop('url')
        with open(json_file, 'w') as fh:
            json.dump(event, fh, sort_keys=True, indent=4, separators=(',', ': '))


main()