import json
import os
import sys
import smtplib
from jinja2 import Environment, PackageLoader

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

env =  Environment(loader=PackageLoader('cat'))
template = env.get_template('email.html')
# add in e-mail from https://docs.python.org/3.4/library/email-examples.html
root = os.path.dirname((os.path.realpath(__file__)))
sys.path.insert(0, root)
from cat import tools
from cat.tools import read_json

with open('subscribers.json', 'r') as fh:
  subscriptions = json.load(fh)

print(subscriptions)

cat = read_json(root + '/html/cat.json')
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
msg['To'] = you

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

#s = smtplib.SMTP('localhost')
#s.sendmail(me, you, msg.as_string())
#s.quit()


with open ("file.txt", "wb") as fout:
    fout.write (bytes(msg))





