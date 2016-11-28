Videos
=========

Major tasks with videos:
* Add the playlists to the events files
* Add more videos
* Add the speakers
* Add tags, update descriptions



Add the playlists to the events files
------------------------------------
Each event has a field called `youtube` that can hold the id of the playlist in YouTube of the videos of that specific event.
Running `python3 video.py` will list all the event that do NOT have a playlist yet.
Check the conference web page and/or search for the name of the conference in YouTub and add the ID of
the playlist to the appropriate `data/events/*` file.

Add more videos
-----------------

We index the videos recorded at events. The videos of event `abc-2000` which is stored at `data/events/abc-2000.txt`
are located in `data/videos/abc-2000`. Each video is represented by a JSON file in that directory. Optionally
each video can also have a .html file (with the same filename as the JSON file has). The content of this HTML file
will be the "description" of the video. The reason we allow external files is to make it easy to spread the
text to multiple lines and to include html tags.

For now we are only indexing videos on YouTube.

Add videos from YouTube
------------------------


Using a forked version of the youtube.py from https://github.com/pyvideo/data/tree/master/tools we can fetch the list of videos from Youtube and create the JSON files.

```python3 tools/youtube.py  -k YOUTUBE_API_KEY  --list YOTUBE_PLAYLIST_ID -d 2016-08-03```

This will create the a directory called ```category-TIMESTAMP``` inside that directory is a subdirectory
called `videos` which needs to be moved to  `conferences/data/videos/abc-2000`.

TODO: further change the Python script to save the length of the video.

Update the videos from YouTube
------------------------------

1) in the `speakers` field add the name of the speaker or speakers in "full-name" format.
The format should only include lower case a-z letters and dash (-).

The name of the speaker usually can be found in title of the talk and/or in the description of the talk.

Check if the file date/people/full-name.txt exist, if not create it and fill it with the appropriate fields.
You can usually find some of the details of the speaker on the web site of the event. From there you can usually
find the other values as well.

```
name:
twitter:
github:
home:
country:
```

2) Remove the name of the speaker and the name (and year) of the conference from the title. Keep just the real title of the talk.
For example if this was the title "Foo Bar - Frobnicating the FuzzBazz - Conference 2016" then it looks like the name
of the speaker is "Foo Bar" and the event is "Conference 2016". We would like the title to be:
"Frobnicating the FuzzBazz"


Run `python3 generate.py --html` to generate the web site and to check if the values in the `speakers` field match the filenames.




Add the speakers
------------------
The videos of these conferences were already added, but the speaker information
has not been added yet:

apachecon-na-2013
apachecon-na-2014
apachecon-na-2015
cloudstack-collaboration-na-2014
deccanrubyconf-2015
devoxx-france-2015
empirenode-2015
fscons-2012
fscons-2013
fscons-2014
fscons-2015
jsconf-eu-2015
jsconf-us-2015
gothamgo-2015
nodeconf-eu-2015
nodevember-2014
nodevember-2015
rubyconf-india-2014
rubyconf-india-2015
pgconfus-2015
postgresopen-2012
postgresopen-2013
postgresopen-2014
postgresopen-2015
rubyfuza-2013
rubyfuza-2014
front-trends-2015
react-conf-2015
linuxfest-northwest-2015

linuxfest-northwest-2016
front-trends-2016
nodeconf-eu-2016
railsconf-2016
devoxx-uk-2016
jsconf-uruguay-2016

laracon-eu-2016
opensourcebridge-2015
polyconf-2016
reactrally-2016
viewsourceconf-berlin-2016

accessibility-camp-new-york-2016
fullstackfest-2015
fullstackfest-2016
gotocon-amsterdam-2016
gotocon-chicago-2016
gotocon-copenhagen-2016
gotocon-stockholm-2016

eclipsesummit-india-2016
functionalconf-2016
seleniumconf-india-2016
seleniumconf-uk-2016
seleniumconf-usa-2015

``` grep speaker * | grep '\[\]' ```

Add tags, update descriptions
-----------------------------


