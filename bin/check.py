#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.code import GenerateSite

gs = GenerateSite()

gs.read_videos()
report = gs.check_videos()
if report != '':
    print(report)

gs.read_people()
report = gs.check_people()
if report != '':
    print(report)

# vim: expandtab

