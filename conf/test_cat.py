from conf.code import GenerateSite
import unittest
import json

class TestDemo(unittest.TestCase):
    def test_generate(self):
        GenerateSite().generate_site()
        assert True


# vim: expandtab
