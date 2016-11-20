import argparse
import os
import json
from datetime import datetime
from jinja2 import Environment, PackageLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_address = 'Code And Talk <blaster@codeandtalk.com>'

# find the videos that have a "featured" key today
# find the 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', '-d', help = 'YYYY-MM-DD Defaults to today')
    parser.add_argument('--to', help = 'Email address to send to')
    args = parser.parse_args()

    if not args.date:
        args.date = datetime.now().strftime('%Y-%m-%d')
    print("Sending for date {}".format(args.date))

    blasters = ['perl', 'javascript']

    featured = []

    for root, dirs, files in os.walk('html/v', topdown=False):
        for f in files:
            if f[-5:] == '.json':
                with open(os.path.join(root, f)) as fh:
                    video = json.loads(fh.read())
                    if video.get('featured', '') == args.date:
                        #print(video['tags'])
                        video['links'] = [ t['link'] for t in video['tags'] ]
                        featured.append(video)
                        
    env = Environment(loader=PackageLoader('conf', 'templates'))
    template = env.get_template('blaster_mail.html')

    #print(featured)
    for bl in blasters:
        entries = []
        for video in featured:
            if bl in video['links']:
                entries.append(video)
        if len(entries) > 0:
            #print(entries) 
            subject = "Featured {} video for {}".format(bl, args.date)
            html = template.render(
                title     = subject,
                entries   = entries,
            )
            to = args.to
            if not to:
                to = bl + '-blaster@codeandtalk.com'

            print("Keyword {} sending to {}  Number of entries {}".format(bl, to, len(entries)))
            #print(html)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_address
            msg['To'] = to

            text = 'No plain text version currrently.'

            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            msg.attach(part1)
            msg.attach(part2)

            s = smtplib.SMTP('localhost')
            s.sendmail(from_address, to, msg.as_string())
            s.quit()

main()

# vim: expandtab
