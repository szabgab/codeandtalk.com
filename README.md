List of tech conferences
==========================

How to add an event:
There is a `skeleton.txt` in the root of the repository. Use that to create the appropriate file in data/

Details of the fields
------------------------

```
name:               The name might need to includ the country/city and theyear. Check similar events.
url:                http://...

start_date:         2016-06-01
end_date:           2016-06-02
cfp_date:           2016-02-23     (Deadline for Call for Presentations if available) 

city:               Name of the city
state:              Relevant in US, Brasil, Australia, India.   Possibly also in UK
country:            Name of the country

topics:             comma separated list
languages:          Portuguese, English
code_of_conduct:    URL to Code of Conduct
accessibility:      URL to document about accessibility
twitter:            handle         (don't include the @)
facebook:
youutube:           Once the event is over, the YouTube playlist of its videos.
```

Generate web site (and check format)
-----------------------------------

$ python3 generate.py


Images
---------
Accessibility logo: http://staff.washington.edu/tft/a11ylogo/

TODO
-----
* For older events: are the videos available online?

* Include logo of each event?
* Improved UI!

* Create separate Twitter account for the site.
* Change the sitemap.xml creating code to use the date of the files for real date.


Other sources
------
https://techpoint.ng/2016/09/14/hackjos-2016-2/

