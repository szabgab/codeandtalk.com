from conf.code import GenerateSite
import unittest
import json
import sys

class TestDemo(unittest.TestCase):
    def test_generate(self):
        GenerateSite().generate_site()
        assert True

    def test_videos(self):
        gs = GenerateSite()
        #gs.read_videos()
        report = gs.check_videos()
        sys.stderr.write(report)
        assert report == ''

    def test_people(self):
        gs = GenerateSite()
        gs.read_people()
        report = gs.check_people()
        sys.stderr.write(report)
        assert report == ''

# vim: expandtab
