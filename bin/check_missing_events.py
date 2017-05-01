#!/usr/bin/env python3

import argparse
import os
import sys

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat.code import GenerateSite

"""
    This utility helps finding missing events for a specified year based on
    already existing events from another year.
    If a reference year is not provided, the year before will be use as the
    reference.
    The logic used is as follow:
    for each event from the reference year :
        if the event URL contains the reference year, change the URL with the
              year to check and try to access the URL
        if not, access the URL from the reference year and search for the year
         to check in the response text
"""

parser = argparse.ArgumentParser(description='CAT Missing Events Helper')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='prints additional information')
parser.add_argument('--reference',
                    help='The year that will be use for reference. '
                         'If not provided we will use the year '
                         'before the one to check', type=int)
parser.add_argument('year',
                    help='The year to check for missing events', type=int)
args = parser.parse_args()

verbosity = args.verbose


def print_debug(msg):
    if verbosity:
        print (msg)

year_to_check = str(args.year)

if args.reference:
    reference_year = str(args.reference)
else:
    reference_year = str(args.year - 1)

print_debug('Year to check: {}'.format(year_to_check))
print_debug('Reference year: {}'.format(reference_year))

site = GenerateSite()
site.read_all()
for event, details in site.events.items():
    if event.endswith(reference_year):
        next_event = event.replace(reference_year, year_to_check)
        if next_event not in site.events:
            print_debug('Checking event {}'.format(next_event))
            url = details['url']
            if url.find(reference_year) != -1:
                new_url = url.replace(reference_year, year_to_check)
                print_debug('Checking changed URL {}'.format(new_url))
                try:
                    response = requests.get(new_url)
                    if response.status_code == 200:
                        print('Potential missing event: {}'.format(next_event))
                        print(new_url)
                    else:
                        pass
                except:
                    pass
            else:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        if response.text.find(year_to_check) != -1:
                            print('Potential missing event: {}'
                                  .format(next_event))
                            print(url)
                    else:
                        pass
                except:
                    pass

# vim: expandtab
