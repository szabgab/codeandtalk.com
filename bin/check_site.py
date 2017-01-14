#!/usr/bin/env python3
import requests

urls = [
	'https://codeandtalk.com/',
	'https://codeandtalk.com/conferences',
	'https://codeandtalk.com/topics',
	
	'https://codeandtalk.com/e/wootconf-2017',
	
	'https://codeandtalk.com/v/react-conf-2016/reactjs-conf-2016-lightning-talks-vivian-cromwell',
	'https://codeandtalk.com/sitemap.xml',
]

for url in urls:
	response = requests.get(url)	
	if response.status_code != 200:
		print("failed {}".format(url))
		print(response.status_code)

