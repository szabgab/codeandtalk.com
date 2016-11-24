#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.code import GenerateSite

# list people who only have their name

gs = GenerateSite()

gs.read_people()
for nickname in gs.people:
    fields = gs.people[nickname]['info'].keys()
    if len(fields) == 1:
        print("{}  https://codeandtalk.com/p/{}".format(gs.people[nickname]['info']['name'], nickname))

# vim: expandtab

