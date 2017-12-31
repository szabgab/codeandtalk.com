import json
import os
import sys
from jinja2 import Environment, PackageLoader

env =  Environment(loader=PackageLoader('cat'))
template = env.get_template('email.html')

root = os.path.dirname((os.path.realpath(__file__)))
sys.path.insert(0, root)
from cat import tools
from cat.tools import read_json

with open('subscribers.json', 'r') as fh:
  subscriptions = json.load(fh)

print(subscriptions)

cat = read_json(root + '/html/cat.json')
conferences = tools.future(cat)

print(template.render(
  events = conferences, title="Hello"
))
