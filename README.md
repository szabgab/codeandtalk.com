###Status
[![Build Status](https://travis-ci.org/szabgab/codeandtalk.com.png)](https://travis-ci.org/szabgab/codeandtalk.org)

List of tech conferences, podcasts, videos, people
==================================================

For more details visit:

https://github.com/szabgab/codeandtalk.com/blob/main/docs/CONFERENCES.md

https://github.com/szabgab/codeandtalk.com/blob/main/docs/VIDEOS.md

https://github.com/szabgab/codeandtalk.com/blob/main/docs/PODCASTS.md

https://github.com/szabgab/codeandtalk.com/blob/main/docs/PEOPLE.md

SETUP
------
```
virtualenv venv3 -p python3
source venv3/bin/activate
pip install flask jinja2
```

Generate web site (and check format)
-----------------------------------

```
$ python3 bin/generate.py
```

Development server
-------------------
```
$ python3 bin/server.py
```

http://localhost:8000/


Application server
--------------------
```
virtualenv venv2 -p /usr/bin/python
source venv2/bin/activate
pip install --editable .

export FLASK_APP=cat.app
export FLASK_DEBUG=1
flask run --host 0.0.0.0 --port 5000
```


TODO
-----
* Describe the use of the site.

* Convert all the data files to JSON, beautidy them.
* Create skeleton for each file-type.

* Include picture of each speaker?
* Include logo of each event?

* Change the sitemap.xml creating code to use the date of the files for real date.
* For sitemap of the collection pages, use the timestamp of the most recent event in that list.
* For sitemap of videos, use the date of the file.

* Update the description of the data and the collection process.

* Search:
  limit the search to people/videos/events/podcasts

* Search for videos
  limit the search by date
  limit the search by language (for videos)

* Search for speakers (or guests for podcast)
  by name
  by words in video tags or video titles or podcast tags or podcast title or topics in personal file
  by location
  by language


* Weekly Newsletter with information about events.
  The subscriber should be able to select filter by countries and/or by topics.
  The e-mail itself is an HTML message that we can also build on the website.

* Add Facebook image code to video pages
* Improve the UI of the web site, look at what pyvideo has nice.
  Font Awesome
* Link from event to other events in the series.

* Another potential use of the data: Help conference and meetup organizers find potential speakers.
* List people by location (city, state, country)
* List people by subjects (tags for which they spoke)

* Add "language" field to the videos and allow the user to filter the results to selected language(s). (There are talk in French, German, Spanish, etc.)


TODO Check for events:
-------------
* http://2016.geecon.cz/
* http://www.qualitysoftware.com.au/ http://www.qualitysoftware.com.au/atd2k16/
* http://europeantestingconference.eu/2017/ https://twitter.com/EuroTestingConf
* http://codecooperative.org/
* https://central.wordcamp.org/
* https://wpcampus.org/
* https://therichwebexperience.com/conference/clearwater/2016/12/home
* http://www.cue.org/conference
* http://www.nodetogether.org/
* https://atscaleconference.com/
* https://jsconf.co/2015-Videos/
* http://rubycentral.org/railsconf

* https://www.youtube.com/channel/UCp2Tsbjd3P8itnBHUNHi82A/playlists
* https://github.com/nodeconf

http://visualized.com/2014/conference/
http://visualized.com/2015
http://visualized.com/2016



Other sources
------
https://techpoint.ng/2016/09/14/hackjos-2016-2/



Some Advice to Conference organizers
--------------------------------------
Just a few random thoughts as I index the videos and the conferences.

* If you record lightning talks, split them up to individual videos. That allows people to watch one short video while at work.
* Include the names of the speakers in the filenames.

* Keep the web site of the previous editions of your event, or at least keep the list of talks and list of people.
* The best would be to have well defined URLs. Some conferences have subdomains per year: http://2017.someevent.com/
Other have them in subdirectory: http://someevent.com/2017/  Both are good.
The best if the main page only redirects to the current event or holds some content, but each event has its own subsite.
Make sure every page of the earlier events have a prominent link at the top linking to the home page of the conference (which can then
redirect to the current or upcoming event).

* On the speaker page include the Twitter and GitHub IDs of each speaker.

