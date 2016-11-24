from cat.code import GenerateSite
import unittest
import json
import os
import sys

def read_json(file):
    with open(file) as fh:
        return json.loads(fh.read())
        #return fh.read()

class TestDemo(unittest.TestCase):
    def test_generate(self):
        GenerateSite().generate_site()
        assert True

        files = [
            'html/v/yougottalovefrontend-2016/vitaly-friedman-cutting-edge-responsive-web-design.json',
        ]
        for result_file in files:
            expected_file = 'samples/' + os.path.basename(result_file)
            #sys.stderr.write(result_file)
            #sys.stderr.write("\n")
            #sys.stderr.write(expected_file)
            #sys.stderr.write("\n")
            # read both files
            result = read_json(result_file)
            expected = read_json(expected_file)
            if result != expected:
                print("Expected: {}".format(expected))
                print("Received: {}".format(result))
            assert result == expected

        # compare them
        

    def test_videos(self):
        gs = GenerateSite()
        gs.read_videos()
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
