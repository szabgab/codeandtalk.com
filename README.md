List of tech conferences
==========================

How to add an event:
There is a skeleton.txt in the root of the repository. Use that to create the appropriate file in data/

Details of the fields
------------------------

```
name:
url:

start_date:         2016-06-01
end_date:
cfp_date:

city:               (Location)
state:
country:

topics:             comma separated list
code_of_conduct:    URL to Code of Conduct
```


Generate web site
--------------------------

$ python3 generate.py


Other - conferences we probably won't include
------------
GPU Technology Conference 2017 http://www.gputechconf.com/ 


TODO
-----
* For older events: are the videos available online?

* Include logo of each event?
* Page per topic.
* Page per country.
* Page per country-state
* page per country-state-city
* page per country-city  (if there is no state)
* Improved UI!

* Create separate Twitter account for the site.
