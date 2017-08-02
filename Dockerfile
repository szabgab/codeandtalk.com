FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
WORKDIR /webapp
COPY requirements.txt /webapp/
RUN pip3 install -r /webapp/requirements.txt

WORKDIR /opt

#ENTRYPOINT ["python"]
#CMD ["app.py"]

# docker build -t codeandtalk .

# docker run -v $(pwd):/opt -it --name cat codeandtalk /bin/bash

# docker start cat && docker attach cat

# EXPOSE 8000
 
# ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--module", "app:app", "--processes", "1", "--threads", "8"]
