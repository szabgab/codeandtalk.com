import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.code import GenerateSite

print(GenerateSite().check_videos())

# vim: expandtab

