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


Sources
---------
https://secure.php.net/conferences/
https://www.papercall.io/cfps
http://www.meetup.com/
http://www.meetup.com/es-ES/Granada-Geek/
https://twitter.com/CallbackWomen/lists/tech-conf-aggregators
https://opensource.com/resources/conferences-and-events-monthly  (but it usually only lists for the next 2 months, not good for call for papers)
http://iteventz.bg/ IT events in Bulgaria
http://sdiwc.net/ The Society of Digital Information and Wireless Communications (SDIWC)
http://droidcon.com/ 
https://www.drupal.org/drupalcon
https://github.com/golang/go/wiki/Conferences
http://events.linuxfoundation.org/


Images
---------
Accessibility logo: http://staff.washington.edu/tft/a11ylogo/


TODO
-----
* For older events: are the videos available online?

* Include logo of each event?
* Page per country.
* Page per country-state
* page per country-state-city
* page per country-city  (if there is no state)
* Improved UI!

* Create separate Twitter account for the site.
* Cron-job to update the site once a day to keep the date-related data fresh.
* Change the sitemap creating code to use the date of the files for real date.

