# How to add an event

Every event is represented by a JSON file in the data/events/ directory.

In order to add a new event you can start by copying the event skeleton file called `data/skeleton-event.json`.
Use that to create the appropriate file in the data/events/ directrory. The filename must reflect the name of the event.
It must be all lowercase and needs to include some identifier of the year and sometimes the location of the event.
(It needs a location if the same event is organized in several places in the world in the same year like devopsdays.)

## Details of the fields in the JSON file

```
{
    "accessibility":            "https://www.devopsdays.org/events/2017-cape-town/",
    "cfp_end":                  "",
    "code_of_conduct":          "https://www.devopsdays.org/events/2017-cape-town/conduct/",
    "comment":                  "",
    "diversitytickets":         "https://www.quicket.co.za/events/22115-devopsdays-cape-town-2017/#/",
    "diversitytickets_text":    "",
    "diversitytickets_url":     "https://www.quicket.co.za/events/22115-devopsdays-cape-town-2017/#/",
    "event_end":                "Tuesday, Nov 7, 2017"  
    "event_start":              "Monday, Nov 6, 2017",
    "facebook":                 "https://www.facebook.com/DevOpsCapeTown",
    "hashtag":                  "",
    "languages": [
                                "English"
    ],
    "location": {
        "city":                 "Hilton Doubletree, Woodstock, Cape Town",
        "country":              "New York",
        "state":                ""
    },
    "name":         "USA/New York /2017.",
    "tags": [
                    "",
    ],
    "twitter":      "https://twitter.com/devopsdays/lists/devopsdays",
    "website":      "https://www.devopsdays.org/events/2017-cape-town/",
    "youtube":      "The YouTube playlist of its videos of the event. Only after the event has ended."
}
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
* Is there a Newsletter?
