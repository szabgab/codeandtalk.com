#!/usr/bin/env python3
import requests

urls = [
	'https://codeandtalk.com/',
	'https://codeandtalk.com/conferences',
	'https://codeandtalk.com/countries',
	'https://codeandtalk.com/cities',
	'https://codeandtalk.com/code-of-conduct',
	'https://codeandtalk.com/diversity-tickets',
	'https://codeandtalk.com/series',
	'https://codeandtalk.com/all-conferences',

	'https://codeandtalk.com/topics',
	'https://codeandtalk.com/t/angularjs',

	'https://codeandtalk.com/podcasts',
	'https://codeandtalk.com/s/changelog',

	'https://codeandtalk.com/people',
	'https://codeandtalk.com/people?term=sz',

	'https://codeandtalk.com/cal/all.ics', # calendar
	
	'https://codeandtalk.com/e/wootconf-2017',
	
	'https://codeandtalk.com/videos',
	'https://codeandtalk.com/videos?term=Hebrew&mindate=&maxdate=&mintime=&maxtime=',
	'https://codeandtalk.com/v/react-conf-2016/reactjs-conf-2016-lightning-talks-vivian-cromwell',
	'https://codeandtalk.com/v/devoxx-france-2016/10-enseignements-quon-peut-tirer-des-31463-commits-qui-ont-cree-le-langage-simone-civetta', # Has Unicode error
	'https://codeandtalk.com/l/goteborg-sweden', # Unicode error
	'https://codeandtalk.com/cal/l/dusseldorf-germany.ics', # Unicode issu?

	'https://codeandtalk.com/about',

	'https://codeandtalk.com/sitemap.xml',
]

failures = []
for url in urls:
	response = requests.get(url)	
	if response.status_code == 200:
		print('    OK     {}'.format(url))
	else:
		failures.append({
			'url'  : url,
			'code' : response.status_code,
		})
		print("NOT OK {:3} {}".format(response.status_code, url))
print("-------------")
if failures:
	print("ERROR")
	print(failures)
else:
	print("SUCCESS")

