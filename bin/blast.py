#!/usr/bin/env python3

import argparse
import os
import json
from datetime import datetime
from jinja2 import Environment, PackageLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite

from_address = 'Code And Talk <blaster@codeandtalk.com>'

# find the videos that have a "featured" key today
# find the 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', '-d', help = 'YYYY-MM-DD Defaults to today')
    parser.add_argument('--to', help = 'Email address to send to')
    parser.add_argument('--dry', help = 'Do not send the messages', action='store_true')
    parser.add_argument('--save', help = 'Save the messages in html files.', action='store_true')
    args = parser.parse_args()

    gs = GenerateSite()

    if not args.date:
        args.date = datetime.now().strftime('%Y-%m-%d')
    print("Sending for date {}".format(args.date))

    gs.read_blasters();

    featured = []

    for root, dirs, files in os.walk('html/v', topdown=False):
        for f in files:
            if f[-5:] == '.json':
                with open(os.path.join(root, f)) as fh:
                    video = json.loads(fh.read())
                    if video.get('featured', '') == args.date:
                        #video['blasters'] = [ t['link'] for t in video['tags'] ]
                        featured.append(video)
                        
    env = Environment(loader=PackageLoader('cat', 'templates'))
    template = env.get_template('blaster_mail.html')

    #print(featured)
    for bl in gs.blasters:
        entries = []
        for video in featured:
            if 'blasters' in video and bl['file'] in video['blasters']:
                entries.append(video)
        if len(entries) > 0:
            #print(entries) 
            subject = "Featured {} video for {}".format(bl['name'], args.date)
            html = template.render(
                title     = subject,
                entries   = entries,
                more      = (len(entries) > 1),
            )
            to = args.to
            if not to:
                to = bl['file'] + '-blaster@codeandtalk.com'

            print("{}: sending to {}  Number of entries {}".format(bl['name'], to, len(entries)))
            send_mail(args, bl['file'], from_address, to, subject, html)

    if len(featured) > 0:
        subject = "All the featured videos for {}".format(bl['name'], args.date)
        html = template.render(
            title     = subject,
            entries   = featured,
            more      = (len(featured) > 1),
        )
        to = args.to
        if not to:
            to = 'master-blaster@codeandtalk.com'
        print("Master: sending to {}  Number of entries {}".format(to, len(featured)))
        send_mail(args, 'master', from_address, to, subject, html)


def send_mail(args, name, from_address, to, subject, html):
    if args.save:
        filename = name + '.html' 
        print("To: {}".format(to))
        print("Subject: {}".format(subject))
        print("saved in {}".format(filename))
        with open(filename, 'w') as out:
            out.write(html)
        return
    if args.dry:
        return

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
