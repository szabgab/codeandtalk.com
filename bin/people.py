#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite

# list people who only have their name

gs = GenerateSite()
gs.generate_site()  #blush
for nickname in gs.people:
    fields = gs.people[nickname]['info'].keys()
    if len(fields) == 1:
        videos = len(gs.people[nickname]['videos'])
        episodes = len(gs.people[nickname]['episodes'])
        hosting = len(gs.people[nickname]['hosting'])
        total = videos + episodes + hosting
        # for now let's only care about people who have at least one something in the database
        # later, when we merge the videos from PerlTV more people will have something
        if total > 0:
            print("{}  https://codeandtalk.com/p/{}".format(gs.people[nickname]['info']['name'], nickname))
        #print(gs.people[nickname])

# vim: expandtab

