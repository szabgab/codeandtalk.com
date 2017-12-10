#!/bin/sh

# A little script to run the dev server. 
# Just run ./startup.sh from the root folder and it should spin up the server
function startServer() {
  virtualenv venv -p python3 &&
  source venv/bin/activate &&
  pip install --editable . &&
  python3 bin/generate.py &&
  FLASK_APP=cat.app FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5000
}

startServer