import os
from xcast.people import GenerateSite

# read all the events
# list the ones that have youtube value which is not - and that does NOT have the video directory.
# list the ones that have no youtube entry or that it is empty

gs = GenerateSite()
gs.read_events()
no_videos = ''
no_youtube = ''
for e in gs.conferences:
    #print(e)
    youtube = e.get('youtube')
    if youtube:
        if youtube != '-':
            if not os.path.exists('data/videos/' + e['nickname']):
                no_videos += "{:30} {}\n".format( e['nickname'], youtube)
    else:
        no_youtube += "{}\n".format( e['nickname'] )

if no_videos:
    print("Has youtube ID but videos were not included")
    print(no_videos)

if no_youtube:
    print("Has no youtube ID")
    print(no_youtube)

# vim: expandtab

