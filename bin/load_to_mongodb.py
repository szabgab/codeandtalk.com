from pymongo import MongoClient
import pymongo
import sys
import os
import json
import glob

# Go over all the data directory and load each file into MongoDB

dbname = 'cat'
client = MongoClient()
db = client[dbname]

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root)
data_dir = os.path.join(root, 'data')
# print(data_dir)

#events = db.events
#for event_file in glob.glob('data/events/*.json'):
#    with open(event_file) as fh:
#        events.insert_one(json.load(fh))

