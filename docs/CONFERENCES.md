How to add an event:
There is a `skeleton.txt` in the root of the repository. Use that to create the appropriate file in data/

Details of the fields
------------------------

```
name:               The name might need to include the country/city and the year. Check similar events.
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
hashtag:            hashtag,if not specified the handle will be used (don't include the #)
facebook:
youtube:           Once the event is over, the YouTube playlist of its videos.

diversitytickets        The id number from https://diversitytickets.org/ 
                        alternatively:
diversitytickets_url    URL describing the diversity option on the conf site
diversitytickets_text   Optional text for the above URL
```

In the `youtube` field use a single - to indicate tha the conference does not have videos on Youtube.

Do not mark in such way conferences that have videos in some other place. We still need to figure out how to include
those.


Questions
------------------
* Is this part of a series of events?
* Are videos available?
* How can we get notified when a new event is scheduled?
* How can we get notified when the videos are posted?
* Newsletter / Twitter / Facebook ?
