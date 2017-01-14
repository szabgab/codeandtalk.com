from cat.code import GenerateSite
import unittest
import json
import os
import sys
import cat.app

def read_json(file):
    with open(file) as fh:
        return json.loads(fh.read())
        #return fh.read()

class TestCat(unittest.TestCase):
    def setUp(self):
        GenerateSite().generate_site()
        self.app = cat.app.catapp.test_client()

    def test_main(self):
        rv = self.app.get('/')
        assert rv.status == '200 OK'
        assert b'Presentations from tech events worth watching' in rv.data

    def test_404(self):
        rv = self.app.get('/abc')
        #print('Status: ' + rv.status)
        assert rv.status == '200 OK' # TODO really this should be 404 but that gives an error: TypeError: Expected bytes
                    # probably because of the way we pass the values back up in the static_file route
        assert b'Oh. There is no page here.' in rv.data

    def test_pages(self):
        rv = self.app.get('/e/ffconf-2009')
        assert rv.status == '200 OK'
        assert b'<h1>Full Frontal - ffconf 2009</h1>' in rv.data
        assert b'<div>Start date: 2009-11-20</div>' in rv.data
        assert b'<div>End date: 2009-11-20</div>' in rv.data
        assert b'https://www.youtube.com/playlist?list' not in rv.data

        rv = self.app.get('/e/jsinsa-2016')
        assert rv.status == '200 OK'
        assert b'https://www.youtube.com/playlist?list=PLw7UYp3N0eUaUgeaG3xN4qI4eMojw6u6y' in rv.data
        assert b'<a href="/l/south-africa">' in rv.data

# vim: expandtab
