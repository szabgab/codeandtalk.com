#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite

GenerateSite().generate_site()

# vim: expandtab
