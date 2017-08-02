import json
import glob
import re

# onetime script to convert the data/people/*.txt files to data/people/*.json files

for txt_file in glob.glob('data/people/*.txt'):
    person = {}
    with open(txt_file, encoding="utf-8") as fh:
       for line in fh:
           line = line.rstrip('\n')
           if re.search(r'\A\s*\Z', line):
               continue 

           if line == '__DESCRIPTION__':
               person['description'] = fh.read()
               break
           try:
               k, v = line.split(':', maxsplit=1)
           except Exception as e:
               print(e)
               print(line)
               exit()
           v = v.strip(' ')
           if k in person:
              raise Exception("Duplicate field '{}' in {}".format(k, txt_file))
           person[k] = v

       if 'topics' in person:
           person['topics'] = re.split(r'\s*,\s*', person['topics'])

    json_file = txt_file[0:-3] + 'json'
    with open(json_file, 'w', encoding="utf-8") as fh:
        json.dump(person, fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

# splitup the topics
