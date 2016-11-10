import glob
import os
import re

def read_people(path):
    people = {}
    for filename in glob.glob(path + "/*.txt"):
        try:
            this = {}
            nickname = os.path.basename(filename)
            nickname = nickname[0:-4]
            with open(filename, encoding="utf-8") as fh:
                for line in fh:
                    line = line.rstrip('\n')
                    if re.search(r'\A\s*\Z', line):
                        continue
                    k,v = re.split(r'\s*:\s*', line, maxsplit=1)
                    this[k] = v
            for field in ['twitter', 'github', 'home']:
                if field not in this:
                    #print("WARN: {} missing for {}".format(field, nickname))
                    pass
                elif this[field] == '-':
                    this[field] = None
            people[nickname] = {
                'info': this,
                'episodes' : [],
                'hosting' : []
            }
        except Exception as e:
            exit("ERROR: {} in file {}".format(e, filename))

    return people

# vim: expandtab

