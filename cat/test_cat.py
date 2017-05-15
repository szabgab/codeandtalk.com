from cat.code import GenerateSite
import unittest
import json
import os
import sys
import cat.app
from pyquery import PyQuery

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
        for url in ('/abc',
                    '/p/jane-doe',
                    '/v/postgresopen-2012/no-video-here',
                    '/v/no-such-event/no-video-here',
                    '/cal/l/nowhere.ics',
                    '/cal/t/no-such-tag.ics',
                    '/l/nowhere',
                    '/s/nocast',
                    '/t/no-such-topic',
                    '/e/no-such-event',
                    ):
            rv = self.app.get(url)
            assert rv.status == '404 NOT FOUND'
            assert b'Oh. There is no page here.' in rv.data
            assert b'<title>Four Oh Four</title>' in rv.data


    def test_pages(self):
        #print("Platform: " + sys.platform)
        rv = self.app.get('/all-conferences')
        assert rv.status == '200 OK'
        d = PyQuery(rv.data)
        p = d("#ffconf-2009")
        #print(p.html())
        assert 'fa-video-camera' not in p.html()
        # <tr id="ffconf-2009">
        #   <td>2009-11-20</td>
        #   <td class="cfp_none"></td>
        #   <td></td>
        #   <td></td>
        #   <td><i class="fa fa-video-camera"></i></td>
        #   <td><a href="/e/ffconf-2009">Full Frontal - ffconf 2009</a></td>
        #   <td>Brighton, England,  <a href="/l/uk">UK</a></td>
        # </tr>

        p = d("#jsinsa-2016")
        assert 'fa-video-camera' in p.html()
        assert 'Johannesburg' in p.html()
        assert 'South Africa' in p.html()


    def test_event(self):
        rv = self.app.get('/e/ffconf-2009')
        assert rv.status == '200 OK'
        assert b'<h1>Full Frontal - ffconf 2009</h1>' in rv.data
        assert b'<div>Start date: 2009-11-20</div>' in rv.data
        assert b'<div>End date: 2009-11-20</div>' in rv.data
        # events with - in the youtube fields should have no link to youtube
        assert b'https://www.youtube.com/playlist?list' not in rv.data
        assert b'<h2>Videos</h2>' not in rv.data

        rv = self.app.get('/e/jsinsa-2016')
        assert rv.status == '200 OK'
        assert b'https://www.youtube.com/playlist?list=PLw7UYp3N0eUaUgeaG3xN4qI4eMojw6u6y' in rv.data
        assert b'<a href="/l/south-africa">' in rv.data
        assert b'<h2>Videos</h2>' in rv.data
        assert b'<a href="/v/jsinsa-2016/feature-toggle-a-js-app-by-charlene-tshitoka">' in rv.data
        assert b'<a href="/p/charlene-tshitoka">Charlene Tshitoka</a>' in rv.data
        self.assertIn(b'<div>No <a href="/diversity-tickets"><b>Diversity Tickets</b></a></div>', rv.data)
        assert b'<h2>Related events:</h2>' in rv.data
        assert b'<a href="/e/jsinsa-2012">jsinsa - JavaScript in South Africa 2012</a>' in rv.data

        rv = self.app.get('/e/mojoconf-2014')
        assert rv.status == '200 OK'
        assert b'<h2>Related events:</h2>' not in rv.data

        rv = self.app.get('/e/script-2017')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<div><a href="https://diversitytickets.org/events/53">Diversity Tickets</a></div>', rv.data)

        rv = self.app.get('/e/cssconf-eu-2017')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<div><a href="http://2017.cssconf.eu/diversity-support-tickets/">Diversity Tickets</a></div>', rv.data)

        rv = self.app.get('/e/fsto-2017')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<div><a href="http://2017.fsto.co/">Diversity Tickets: see under pricing</a></div>', rv.data)

    
    def test_featured(self):
        rv = self.app.get('/featured')
        assert rv.status == '200 OK'
        assert b'<a href="/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016">' in rv.data

        rv = self.app.get('/featured-by-date')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<a href="/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016">', rv.data)

    def test_video_pages(self):
        rv = self.app.get('/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<title>Javascript Minus Javascript</title>', rv.data)
        #print(rv.data)

        rv = self.app.get('/v/devoxx-france-2016/10-enseignements-quon-peut-tirer-des-31463-commits-qui-ont-cree-le-langage-simone-civetta')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<title>10 enseignements qu&#39;on peut tirer des 31.463 commits qui ont cr\xc3\xa9\xc3\xa9 le langage (French)</title>', rv.data)
        #print(rv.data)

        rv = self.app.get('/l/goteborg-sweden')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<title>Conferences in b&#39;Gteborg, Sweden&#39;</title>', rv.data)
        #print(rv.data)

    def test_calendar(self):
        rv = self.app.get('/cal/all.ics')
        self.assertEqual(rv.status, '200 OK')
        rv = self.app.get('/cal/l/dusseldorf-germany.ics')
        self.assertEqual(rv.status, '200 OK')

    def test_podcast_participants(self):
        rv = self.app.get('/s/cmos')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<a href="/p/jason-crome">Jason A. Crome</a>', rv.data)
        self.assertIn('<a href="/p/gabor-szabo">Gábor Szabó</a>'.encode('utf-8'), rv.data)

    def test_people(self):
        rv = self.app.get('/people')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<title>People who talk at conferences or in podcasts</title>', rv.data)

        rv = self.app.get('/people?term=sz')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn(b'<title>People who talk at conferences or in podcasts</title>', rv.data)
        self.assertIn(b'<a href="/p/jakub-jedryszek">Jakub Jedryszek</a>', rv.data)
        self.assertIn('<a href="/p/gabor-szabo">Gábor Szabó</a>'.encode('utf-8'), rv.data)

        rv = self.app.get('/p/gabor-szabo')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn('<title>Presentations and podcasts by Gábor Szabó</title>'.encode('utf-8'), rv.data)
        assert b'<li>2016-08-23 <a href="http://code-maven.com/cmos-1-jason-crome-perl-dancer2">Jason A. Crome on Perl Dancer 2</a> <a href="/s/cmos">cmos</a></li>' in rv.data


        rv = self.app.get('/p/adam-stacoviak')
        self.assertEqual(rv.status, '200 OK')
        assert b'<li>2015-10-12 <a href="http://www.codenewbie.org/podcast/podcasting-with-changelog">Podcasting with Changelog</a> <a href="/s/codenewbie">codenewbie</a></li>' in rv.data
        assert b'<li>2009-11-27 <a href="https://changelog.com/3/">The Go Programming Language from Google with Rob Pike</a> <a href="/s/changelog">changelog</a></li>', rv.data

# vim: expandtab
