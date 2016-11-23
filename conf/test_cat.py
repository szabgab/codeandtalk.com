from conf.code import GenerateSite
import unittest
import json
import sys

class TestDemo(unittest.TestCase):
    def test_generate(self):
        GenerateSite().generate_site()
        assert True

    def test_videos(self):
        report = GenerateSite().check_videos()
        sys.stderr.write(report)
        assert report == ''


# vim: expandtab
