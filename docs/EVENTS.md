How to add an event:
There is a file called `data/skeleton-event.json`. Use that to create the appropriate file in data/events/

Details of the fields
------------------------

```
name:               The name might need to include the country/city and the year. Check similar events.
                    It should end with the year of the event. (e.g. 2016)
website:            http://...

event_start:         2016-06-01
event_end:           2016-06-02
cfp_end:             2016-02-23     (Deadline for Call for Presentations if available)

city:               Name of the city
state:              Relevant in US, Brasil, Australia, India.   Possibly also in UK
country:            Name of the country (from the list in data/countries.csv)

tags:               comma separated list of lower-case strings (in double quotes) taken from data/tags.json
languages:          Portuguese, English
code_of_conduct:    URL to Code of Conduct
accessibility:      URL to document about accessibility
twitter:            handle         (don't include the @)
hashtag:            hashtag, if not specified the handle will be used (don't include the #)
facebook:           include entire URL
youtube:            Once the event is over, the YouTube playlist of its videos.

diversitytickets        The id number from https://diversitytickets.org/
                        alternatively:
diversitytickets_url    URL describing the diversity option on the conf site
diversitytickets_text   Optional text for the above URL
```

In the `youtube` field of past events use a single dash `-` to indicate that the conference does not have videos on Youtube.
If you don't know, leave the field empty.

Do not mark in such way conferences that have videos in some other place. We still need to figure out how to include
those.


Questions
------------------
* Is this part of a series of events?
* Are videos available?
* How can we get notified when a new event is scheduled?
* How can we get notified when the videos are posted?
* Newsletter / Twitter / Facebook ?
