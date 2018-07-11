FROM ubuntu:17.10
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y uwsgi uwsgi-plugin-python3
WORKDIR /webapp
COPY requirements.txt /webapp/
RUN pip3 install --no-cache-dir -r /webapp/requirements.txt

WORKDIR /opt

ENV LC_ALL      C.UTF-8
ENV LANG        C.UTF-8
ENV PYTHONPATH  /opt

COPY codeandtalk.ini /etc/uwsgi/apps-enabled/

# Build the Docker image:
# docker build -t codeandtalk .

# docker run -v $(pwd):/opt -it -p 5000:5000 --name cat codeandtalk /bin/bash

# docker run -v $(pwd):/opt -d -p 5000:5000 --name cat codeandtalk uwsgi /etc/uwsgi/apps-enabled/codeandtalk.ini

# docker start cat && docker attach cat

EXPOSE 5000
#ENTRYPOINT ["service", "uwsgi", "start"]
 
# ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--module", "app:app", "--processes", "1", "--threads", "8"]
