import json
import logging
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, PackageLoader

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



env =  Environment(loader=PackageLoader('cat'))
template = env.get_template('email.html')
# add in e-mail from https://docs.python.org/3.4/library/email-examples.html
root = os.path.dirname((os.path.realpath(__file__)))
sys.path.insert(0, root)
from cat import tools
from cat.tools import read_json

with open('subscribers.json', 'r') as fh:
  subscriptions = json.load(fh)

logger.debug(subscriptions)

db_file = root + '/html/cat.json'

cat = read_json(db_file)
if not 'events' in cat:
    raise ValueError("key events is missing in {}, please generate db file (see readme)".format(db_file))

conferences = tools.future(cat)

html =template.render(
  events = conferences, title="Hello"
)

text = "Hello"
me = "me@email"
you = "me@email"


msg = MIMEMultipart('alternative')
msg['Subject'] = "Upcoming Events"
msg['From'] = me

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('localhost')
for subs in subscriptions:
    to = subs['email']
    msg['To'] =  '{name} <{email}>'.format(**subs)
    logger.debug(msg)
    s.sendmail(me, to, msg.as_string())
s.quit()


# with open ("file.txt", "wb") as fout:
#     fout.write (bytes(msg))





