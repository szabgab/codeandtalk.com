#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.code import GenerateSite

gs = GenerateSite()
print(gs.check_videos())
gs.read_people()
print(gs.check_people())

# vim: expandtab

