#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite, CATerror

try:
    GenerateSite().generate_site()
except CATerror as e:
    print(e)
    exit(1)

# vim: expandtab
