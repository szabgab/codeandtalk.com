from cat.code import GenerateSite
import pytest
import json
import os
import sys
import cat.app
from pyquery import PyQuery
import shutil

def read_json(file):
    with open(file) as fh:
        return json.loads(fh.read())
        #return fh.read()



class TestCat(object):
    def setup_class(self):
        if 'CAT_TEST' in os.environ:
            os.environ.pop('CAT_TEST')
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
        #self.assertTrue (False, msg=d)
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

    def test_topic_links (self):
        rv = self.app.get('/topics')
        assert rv.status == '200 OK'

        #import code
        #code.interact(local=locals())

        #rv = self.app.get('/t/accessibility')
        #assert rv.status == '200 OK'

        found_0 = 0
        found_non_0 = 0
        page_html = PyQuery(rv.data)
        table_lines = page_html("#topics tr")
        for i in range (1, len (table_lines)):  
            tr = table_lines[i]      
            tds = tr.getchildren()
            td2 = tds[1]
            td1 = tds[0]
            a_list = tds[0].getchildren()
            a = a_list[0]
            href = a.attrib['href']
            if td2.text == '0':
                found_0 += 1
            else:
                found_non_0 += 1

            topic = self.app.get(href)
            assert topic.status == '200 OK'

            if found_0 > 0 and found_non_0 > 0:
                break
        
       
    def test_event(self):
        rv = self.app.get('/e/ffconf-2009')
        assert rv.status == '200 OK'
        assert b'<title>Full Frontal - ffconf 2009</title>' in rv.data
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
        assert b'<div>No <a href="/diversity-tickets"><b>Diversity Tickets</b></a></div>' in rv.data
        assert b'<h2>Related events:</h2>' in rv.data
        assert b'<a href="/e/jsinsa-2012">JavaScript in South Africa 2012</a>' in rv.data

        rv = self.app.get('/e/mojoconf-2014')
        assert rv.status == '200 OK'
        assert b'<h2>Related events:</h2>' not in rv.data

        rv = self.app.get('/e/script-2017')
        assert rv.status == '200 OK'
        assert b'<div><a href="https://diversitytickets.org/events/53">Diversity Tickets</a></div>' in rv.data

        rv = self.app.get('/e/cssconf-eu-2017')
        assert rv.status == '200 OK'
        assert b'<div><a href="http://2017.cssconf.eu/diversity-support-tickets/">Diversity Tickets</a></div>' in rv.data

        rv = self.app.get('/e/fsto-2017')
        assert rv.status == '200 OK'
        assert b'<div><a href="http://2017.fsto.co/">Diversity Tickets: see under pricing</a></div>' in rv.data

    
    def test_featured(self):
        rv = self.app.get('/featured')
        assert rv.status == '200 OK'
        assert b'<a href="/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016">' in rv.data

        rv = self.app.get('/featured-by-date')
        assert rv.status == '200 OK'
        assert b'<a href="/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016">' in rv.data

    def test_video_pages(self):
        rv = self.app.get('/v/cascadiafest-2016/sarah-meyer-javascript-minus-javascript-cascadiafest-2016')
        assert rv.status == '200 OK'
        assert b'<title>Javascript Minus Javascript</title>' in rv.data
        #print(rv.data)

        rv = self.app.get('/v/devoxx-france-2016/10-enseignements-quon-peut-tirer-des-31463-commits-qui-ont-cree-le-langage-simone-civetta')
        assert rv.status == '200 OK'
        assert b'<title>10 enseignements qu&#39;on peut tirer des 31.463 commits qui ont cr\xc3\xa9\xc3\xa9 le langage (French)</title>' in rv.data
        #print(rv.data)

        rv = self.app.get('/l/goteborg-sweden')
        assert rv.status == '200 OK'
        assert b'<title>Conferences in b&#39;Gteborg, Sweden&#39;</title>' in rv.data
        #print(rv.data)

    def test_calendar(self):
        rv = self.app.get('/cal/all.ics')
        assert rv.status == '200 OK'
        rv = self.app.get('/cal/l/dusseldorf-germany.ics')
        assert rv.status == '200 OK'

    def test_podcast_participants(self):
        rv = self.app.get('/s/cmos')
        assert rv.status == '200 OK'
        assert b'<a href="/p/jason-crome">Jason A. Crome</a>' in rv.data
        assert '<a href="/p/gabor-szabo">Gábor Szabó</a>'.encode('utf-8') in rv.data

    def test_people(self):
        rv = self.app.get('/people')
        assert rv.status == '200 OK'
        assert b'<title>People who talk at conferences or in podcasts</title>' in rv.data

        rv = self.app.get('/people?term=sz')
        assert rv.status == '200 OK'
        assert b'<title>People who talk at conferences or in podcasts</title>' in rv.data
        assert b'<a href="/p/jakub-jedryszek">Jakub Jedryszek</a>' in rv.data
        assert '<a href="/p/gabor-szabo">Gábor Szabó</a>'.encode('utf-8') in rv.data

        rv = self.app.get('/p/gabor-szabo')
        assert rv.status == '200 OK'
        assert '<title>Presentations and podcasts by Gábor Szabó</title>'.encode('utf-8') in rv.data
        assert b'<li>2016-08-23 <a href="http://code-maven.com/cmos-1-jason-crome-perl-dancer2">Jason A. Crome on Perl Dancer 2</a> <a href="/s/cmos">cmos</a></li>' in rv.data


        rv = self.app.get('/p/adam-stacoviak')
        assert rv.status == '200 OK'
        assert b'<li>2015-10-12 <a href="http://www.codenewbie.org/podcast/podcasting-with-changelog">Podcasting with Changelog</a> <a href="/s/codenewbie">codenewbie</a></li>' in rv.data
        assert b'<li>2009-11-27 <a href="https://changelog.com/3/">The Go Programming Language from Google with Rob Pike</a> <a href="/s/changelog">changelog</a></li>' in rv.data

    def test_sitemap(self):
        rv = self.app.get('/sitemap.xml')
        assert rv.status == '200 OK'
        assert b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in rv.data


class TestValidation(object):
    def test_locations(self):
        errors = [
            'ERROR 1: The value of city "OrlandoX" is not in our list. If this was not a typo, add it to data/locations.json. Found in',
            'ERROR 1: The value of state "FloridaX" is not in our list. If this was not a typo, add it to data/locations.json. Found in',
            'ERROR 1: The value of country "USAX" is not in our list. If this was not a typo, add it to data/locations.json. Found in',
            'ERROR 1: Tag "blabla" is not in the list of tags found in data/tags.json. Check for typo. Add new tags if missing from our list. in file'
        ]
        for d in [1, 2, 3, 4]:
            for filename in ['locations.json', 'series.json', 'tags.json']:
                shutil.copyfile(os.path.join('data', filename), os.path.join('test_data', str(d), filename))
            os.environ['CAT_TEST'] = os.path.join('test_data', str(d))
            with pytest.raises(SystemExit) as err:
                GenerateSite().generate_site()
            assert errors[d-1] in str(err.value)

# vim: expandtab
