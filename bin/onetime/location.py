import json
import glob


# one time script updating the event files  move city, state, country inside location
def main():
    for json_file in glob.glob("data/events/*.json"):
        with open(json_file) as fh:
            event = json.load(fh)
        event['location'] = {
            'country': event.pop('country'),
            'state': event.pop('state'),
            'city': event.pop('city'),
        }
        with open(json_file, 'w') as fh:
            json.dump(event, fh, sort_keys=True, indent=4, separators=(',', ': '))


main()