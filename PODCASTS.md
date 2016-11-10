The data in this repository is presented at http://xcast.szabgab.com/

The list of podcasts can be found in ```data/sources.json```.
Each podcast has its own json file in the ```data/``` directory in which we list the episodes.
The name of the podcast is the name of the appropriate JSON file.
For example the episodes of the ```cmos``` podcast are listed in the ```data/cmos.json``` file.

For each episode in a podcast series we collect the following fields:

ep - the episode number
guests:   a list of the guest, each guest is represented her/his name in full-name  format.

The same value, followed by the .txt extension is used to hold information about that person
in the ```data/people/``` directory.
So if the person is called "Foo Bar Qux" then the file name will be ```foo-bar-qux.txt```

```
hosts:     A list of the hosts. Just like the list of the guest.
keywords:  A list of words (e.g. project names) that are important in the episode.
           These should be the names of the project, (e.g. Dancer) or words describing the field such as
           "web", "desktop", "gui", "DevOps".
permalink: The URL of the episode.
title:     The title of the episode.
date:      The date of the episode.
```

The file looks like this:

```
[
  {
    "ep" : "EPISODE NUMBER",
    "guests": {
      "guest-name" : {}
    },
    "hosts" : {
        "host-name" : {}
    },
    "keywords": ["perl", "web", "dancer"],
    "permalink": "URL of the HTML page of the specific episode",
    "title" : "TITLE of the episodes",
    "date": "2016-08-23"
  },
  ...
]
```

Each person (both guests and hosts) have their own file in the ```data/people/``` directory.
These are text files in "field:value" format.

For each person we collect the following 4 fields, but some people might not have all 4:

```
name:      Full name
twitter:   account ID
github:    accoung ID
home:      URL of their personal home page
country:   Country name
```

The ```data/tags.csv``` file contains a mapping of keywords to URLs and descriptions.
This is mostly relevant for keywords that describe a spefic project (e.g. Dancer)
but not for generic keywords such as "web".

```
keyword;http://...
```

Collection Process
-------------------
* Select the podcast you'd like to process. (e.g 'cmos' stored in data/cmos.json).
* Visit the main web-site of the process. (the URL can be found in the data/sources.json file).
* Find the next episode that has not been recorded in the data file. (data/cmos.json in our example).
* Find out the details need to be collected. (See the list of details above at the description of the files.)
* Save the data in the json file (data/cmos.json in our example)
* Save the information about the individual people in the (data/people/*.txt) file.
* Add the files to git, commit, push, send a pull-request.

* If you have a local copy of all the files, you can veryfy the correctness of
the format by running ```python3 xcast.py --html``` fFor this you'll have ```python3```
installed and the ```jinja2``` package.


Site layout
------------
```
/
/p/person-code
/s/source
/t/tag
```

TODO (or maybe not?):
-----------------------
* fetch and fill data about changelog, codenewbie, talkpython
* Create sitemap.xml

* Include the episode number for each episode
* Add the GitHub/Twitter username of each person and the "home" page of each person.
* For each source add a description.
* Include talks from conferences
* Include screencasts and other non-conference videos.
* Include a picture of each person?
* The Floss Weekly had a lot of other "providers" to subscribe through. Check those out.
* The Floss Weekly has both an audio and video feed. Some other podcast might have too. Shall we include those too?
* Add Forkme on GitHub badge


SETUP
------
```
virtualenv venv3 -p python3
source venv3/bin/activate
pip install jinja2
```

Development server
-------------------
```python3 server.py```

http://localhost:8000/


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




Process with command line Git client
----------------------------
* In the GitHub interface visit the project https://github.com/szabgab/xcast and click on the "Fork" button (top righ).
It will create a copy in your own user. IF you are called ```foobar``` it will be called https://github.com/foobar/xcast

* On your command line (Linux terminal or Windows Cmd) type in

```git clone git@github.com:foobar/xcast.git```

It will clone (copy) the whole repository from your GitHub homedirectory.

```cd xcast```

```git remote add upstream https://github.com/szabgab/xcast.git```

Now you can edit the files in the ```xcast/data``` directory and add more files you need.

If you'd like to check if the files work well together type in

```python xcast.py --html``` on windows or ```python3 xcast.py --html``` on Linux.



Instruction on Windows
----------------------
* Install Python 3.x.x from https://www.python.org/downloads/windows/
* Open the command window (Start/Run 'cmd')
* Type in ```python --version``` to check if the installation worked as expected. It should say something like "Python 3.5.2"
  If it says "`Python` is not recognized as an internal or external command, operable program or batch file"
  then you need to configure the PATH environment variable to include the directory of python.exe
  One way is to enter the following in the command prompt: just replace 'gabor' with your username:
  ```set PATH=C:\Users\gabor\AppData\Local\Programs\Python\Python35-32\;%PATH%```
  Then try ```python --version``` again.

* Type in ```pip install jinja2```
* cd to the xcast/ directory 
* Type ```python xcast.py --html```   If there is an error in the files, it will complain.
* If everything works fine the web site is generated in the html/ directory.
* Run ```python server.py``` then go to your broser and visit http://127.0.0.1:8000/  The updated site should be there.






