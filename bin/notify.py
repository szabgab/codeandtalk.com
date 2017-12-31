import json

with open('subscribers.json', 'r') as fh:
  subscriptions = json.load(fh)

print(subscriptions)