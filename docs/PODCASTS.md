The list of podcasts can be found in ```data/sources.json```.
Each podcast has its own json file in the ```data/podcasts/``` directory in which we list the episodes.
The name of the podcast is the name of the appropriate JSON file.
For example the episodes of the ```cmos``` podcast are listed in the ```data/podcasts/cmos.json``` file.

For each episode in a podcast series we collect the following fields:

```commandline
ep:      the episode number
guests:  a list of the guests, each guest is represented her/his name in "full-name" format.
```

The same value, followed by the .json extension is used to hold information about that person
in the ```data/people/``` directory.
So if the person is called "Foo Bar Qux" then the file name will be ```foo-bar-qux.json```

```
hosts:     A list of the hosts. Just like the list of the guest.
keywords:  A list of words (e.g. project names) that are important in the episode.
           These should be the names of the project, (e.g. Dancer) or words describing the field such as
           "web", "desktop", "gui", "DevOps".
permalink: The URL of the episode.
title:     The title of the episode.
date:      The date of the episode.
```

The file looks like this: (but see #221)

```
[
  {
    "ep" : "EPISODE NUMBER",
    "guests": [
      "guest-name"
    ],
    "hosts" : [
        "host-name"
    ],
    "keywords": ["perl", "web", "dancer"],
    "permalink": "URL of the HTML page of the specific episode",
    "title" : "TITLE of the episodes",
    "date": "2016-08-23"
  },
  ...
]
```

Each person (both guests and hosts) have their own file in the ```data/people/``` directory.
See the [People](docs/PEOPLE.md) for the description of the people files.

```

See also [Tags](docs/TAGS.md)

Collection Process
-------------------
* Select the podcast you'd like to process. (e.g 'cmos' stored in data/cmos.json).
* Visit the main web-site of the process. (the URL can be found in the data/sources.json file).
* Find the next episode that has not been recorded in the data file. (data/cmos.json in our example).
* Find out the details need to be collected. (See the list of details above at the description of the files.)
* Save the data in the json file (data/cmos.json in our example)
* Save the information about the individual people in the (data/people/*.json) file.
* Add the files to git, commit, push, send a pull-request.

* If you have a local copy of all the files, you can veryfy the correctness of
the format by running ```python3 bin/generate.py```


TODO (or maybe not?):
-----------------------

* The Floss Weekly had a lot of other "providers" to subscribe through. Check those out.
* The Floss Weekly has both an audio and video feed. Some other podcast might have too. Shall we include those too?


Other sources we might add
----------------------------
* http://www.meta-cast.com/
* http://www.angryweasel.com/ABTesting/
* Start Here Ruby on Rails http://starthere.fm/category/rubyonrails   or http://starthere.fm/ ?
* Start here Web development: http://starthere.fm/category/webdev
* Lately in JavaScript podcast http://www.jsclasses.org/blog/category/podcast/
* ReactJS https://itunes.apple.com/us/podcast/react-podcast/id995869265?mt=2
* IBM Rational talks to you http://www-01.ibm.com/software/rational/podcasts/2014/index.html
* Programming Throwdown https://itunes.apple.com/us/podcast/programming-throwdown/id427166321?mt=2
* The Treehouse show https://itunes.apple.com/us/podcast/the-treehouse-show-hd/id623064192?mt=2
* Android Devlopers Backstage https://itunes.apple.com/us/podcast/android-developers-backstage/id785545036?mt=2
* Simple Programmer Podcast https://itunes.apple.com/us/podcast/simple-programmer-podcast/id998357224



