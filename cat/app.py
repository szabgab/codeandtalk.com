from flask import Flask, render_template, redirect, abort, request, url_for, Response, jsonify
import os
import json
import re

catapp = Flask(__name__)
root = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))


@catapp.route("/people")
def people():
	term = _term()
	ppl = _read_json(root + '/html/people.json')
	result = {}
	if term != '':
		for nickname in ppl.keys():
			if not ppl[nickname]['location']:
				ppl[nickname]['location'] = '-'
			if not ppl[nickname]['topics']:
				ppl[nickname]['topics'] = '-'

			if re.search(term, ppl[nickname]['name'].lower()):
				result[nickname] = ppl[nickname]
			elif re.search(term, ppl[nickname]['location'].lower()):
				result[nickname] = ppl[nickname]
			elif re.search(term, ppl[nickname]['topics'].lower()):
				result[nickname] = ppl[nickname]

	return render_template('people.html',
		title            = 'People who talk at conferences or in podcasts', 
		h1               = 'People who talk',
		number_of_people = len(ppl.keys()),
		term             = term,
		people           = result,
		people_ids       = sorted(result.keys()),
	)

@catapp.route("/search")
def search():
	res = _search()
	return render_template('search.html', **res)

@catapp.route("/api1/search")
def api_search():
	res = _search()
	return jsonify(res)

### static page for the time of transition
@catapp.route("/")
@catapp.route("/<filename>")
def static_file(filename = None):
	#index.html  redirect

	if not filename:
		filename  = 'index.html'
	mime = 'text/html'
	content = _read(root + '/html/' + filename)
	if filename[-4:] == '.css':
		mime = 'text/css'
	elif filename[-5:] == '.json':
		mime = 'application/javascript'
	elif filename[-3:] == '.js':
		mime = 'application/javascript'
	elif filename[-4:] == '.xml':
		mime = 'text/xml'
	elif filename[-4:] == '.ico':
		mime = 'image/x-icon'
	return Response(content, mimetype=mime)


@catapp.route("/p/<person>")
@catapp.route("/t/<tag>")
@catapp.route("/e/<event>")
@catapp.route("/l/<location>")
@catapp.route("/s/<source>")
@catapp.route("/v/<event>/<video>")
@catapp.route("/blaster/<blaster>")
def html(person = None, event = None, video = None, source = None, tag = None, location = None, blaster = None):
	if blaster:
		return _read(root + '/html/blaster/' + blaster)
	if location:
		return _read(root + '/html/l/' + location)
	if source:
		return _read(root + '/html/s/' + source)
	if event:
		return _read(root + '/html/e/' + event)
	if person:
		return _read(root + '/html/p/' + person)
	if video:
		return _read(root + '/html/v/{}/{}'.format(event, video))
	if tag:
		return _read(root + '/html/t/' + tag)

###### Helper functions

def _read(filename):
	try:
		return open(filename).read()
	except Exception:
		return open(root + '/html/404.html').read()
		
def _term():
	term = request.args.get('term', '')
	term = term.lower()
	term = re.sub(r'^\s*(.*?)\s*$', r'\1', term)
	return term

def _search():
	term = _term()
	search_data = _read_json(root + '/html/search.json')
	results = {}
	max_hit_count = 50
	hit_count = 0
	if term != '':
		for k in search_data:
			if re.search(term, k.lower()):
				hit_count += 1
				if hit_count <= max_hit_count:
					results[k] = search_data[k]
	else:
		hit_count = len(search_data.keys())

	return { "term" : term, "results" : results, "total" : hit_count }

def _read_json(filename):
	catapp.logger.debug("Reading '{}'".format(filename))
	try:
		with open(filename) as fh:
			search_data = json.loads(fh.read())
	except Exception as e:
		catapp.logger.error("Reading '{}' {}".format(search_file, e))
		search_data = {}
		pass
	return search_data





