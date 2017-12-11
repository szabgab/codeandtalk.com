#!/bin/sh

# A little script to help automate the process of spinning up a dev server

function startup() {
  virtualenv venv -p python3 &&
  source venv/bin/activate &&
  pip install --editable . &&
  python3 bin/generate.py &&
  FLASK_APP=cat.app FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5000
}

startup