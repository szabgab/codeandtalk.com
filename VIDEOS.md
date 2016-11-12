How to add videos
==================

We index the videos recorded at events. The videos of event `abc-2000` which is stored at `data/events/abc-2000.txt`
are located in `data/videos/abc-2000`. Each video is represented by a JSON file in that directory.

For now we are only indexing videos on YouTube.


Add videos from YouTube
------------------------

Each event ha a field called `youtube` that holds (or should hold) the id of the playlist in YouTube of the videos of that specific event.

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

