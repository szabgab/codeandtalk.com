from flask import Flask, render_template, redirect, abort, request, url_for, Response, jsonify
import os
import json
import re

catapp = Flask(__name__)
root = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))


@catapp.route("/")
def main():
    return """
<a href="/search">search</a>
"""

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


@catapp.route("/people")
def people():
	term = _term()
	ppl = _read_json(root + '/html/people.json')
	result = {}
	if term != '':
		for nickname in ppl.keys():
			if re.search(term, ppl[nickname]['name'].lower()):
				result[nickname] = ppl[nickname]
				if not result[nickname]['location']:
					result[nickname]['location'] = '-'
				continue

	return render_template('people.html', 
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

### static page for the time of transition
@catapp.route("/style.css")
def css():
	return Response(open(root + '/html/style.css').read(), mimetype='text/css')

