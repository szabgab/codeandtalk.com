from flask import Flask, render_template, redirect, abort, request, url_for, Response, jsonify
import os
import json
import re

catapp = Flask(__name__)

search_file = 'html/search.json'
#search_file_time = 0
#search_data = {}

@catapp.route("/")
def main():
    return """
<a href="/search">search</a>
<hr>
Search API:
<form action="/api1/search">
<input name="term">
<input type="submit" value="Search">
</form>
"""

@catapp.route("/search")
def search():
	res = _search()
	return render_template('search.html', **res)

@catapp.route("/api1/search")
def api_search():
	res = _search()
	return jsonify(res)

def _search():
	term = request.args.get('term', '')
	term = term.lower()
	file_time = os.path.getmtime(search_file)
	#if file_time > search_file_time:
	catapp.logger.debug("Reading '{}'".format(search_file))
	#	search_file_time = file_time
	try:
		with open(search_file) as fh:
			new_search_data = json.loads(fh.read())
			search_data = new_search_data
	except Exception as e:
		catapp.logger.error("Reading '{}' {}".format(search_file, e))
		pass
	results = {}
	max_hit_count = 10
	hit_count = 0
	for k in search_data:
		if re.search(term, k.lower()):
			hit_count += 1
			if hit_count <= max_hit_count:
				results[k] = search_data[k]


	return { "term" : term, "results" : results, "total" : hit_count }

