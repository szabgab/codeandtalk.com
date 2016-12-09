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

        # This fails on travis, we probably need better reporting to see what is the actual difference
        # as I cannot see it. Unless it is only the file_date
        files = [
            'html/v/yougottalovefrontend-2016/vitaly-friedman-cutting-edge-responsive-web-design.json',
            'html/p/zohar-babin.json',
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
            if 'file_date' in expected:
                del(expected['file_date'])
                del(result['file_date'])
            if result != expected:
                print("While testing {}\n".format(result_file))
                print("Expected: {}".format(expected))
                print("Received: {}".format(result))
            assert result == expected

# vim: expandtab
