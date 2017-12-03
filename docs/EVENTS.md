# How to add an event

Every event is represented by a JSON file in the data/events/ directory.

In order to add a new event you can start by copying the event skeleton file called `data/skeleton-event.json`.
Use that to create the appropriate file in the data/events/ directrory. The filename must reflect the name of the event.
It must be all lowercase and needs to include some identifier of the year and sometimes the location of the event.
(It needs a location if the same event is organized in several places in the world in the same year like devopsdays.)

## Details of the fields in the JSON file

```
{
    "accessibility":            "URL to document about accessibility",
    "cfp_end":                  "2016-02-23     (Deadline for Call for Presentations if available. Leave it empty if you can't find a CFP)",
    "code_of_conduct":          "URL to Code of Conduct if there is one",
    "comment":                  "",
    "diversitytickets":         "The id number from https://diversitytickets.org/    alternatively:",
    "diversitytickets_text":    "Optional text for the diversitytickets_url",
    "diversitytickets_url":     "URL describing the diversity option on the conf site",
    "event_end":                "2017-11-12   (please note 'event_end' is before 'event_start' here because they are in abc order)",
    "event_start":              "2017-11-10",
    "facebook":                 "include entire URL",
    "hashtag":                  "Twitter hashtag, if not specified the Twitter handle will be used (don't include the #)",
    "languages": [
                                "English", "French"
    ],
    "location": {              (verified with the list in data/locations.json if missing from that list add that too!)
        "city":                 "Name of the city",
        "country":              "Name of the country",
        "state":                "Relevant in US, Brasil, Australia, India, and UK"
    },
    "name":         "The name might need to include the country/city and the year. Check similar events.",
    "tags": [
                    "comma separated list of lower-case strings (in double quotes) taken from data/tags.json",
    ],
    "twitter":      "handle         (don't include the @)",
    "website":      "This is the URL of the event.",
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
