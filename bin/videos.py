# Go over all the JSON files representing videos and check validity
#   Check if they have a "recorded" field with a YYYY-MM-DD timestamp - report if not
#   Check if they have values for "speakers" - report if not
#   Check if they have embedded HTML in the description field (they should be moved out to a separate file)

import glob
import json
import os
import re

def main():
    for event in os.listdir('data/videos'):
        #print(event)
        for video_file in glob.glob('data/videos/' + event + '/*.json'):
            with open(video_file) as fh:
                video = json.loads(fh.read())
                if not re.search(r'^\d\d\d\d-\d\d-\d\d$', video['recorded']):
                    print("Invalid 'recorded' field: {:20} {}  ".format(video['recorded'], video_file))
                #exit(video)
            


main()

# vim: expandtab

