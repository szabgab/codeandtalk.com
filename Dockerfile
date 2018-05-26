FROM ubuntu:17.10
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
WORKDIR /webapp
COPY requirements.txt /webapp/
RUN pip3 install -r /webapp/requirements.txt

WORKDIR /opt

#ENTRYPOINT ["python"]
#CMD ["app.py"]

# Build the Docker image:
# docker build -t codeandtalk .

# docker run -v $(pwd):/opt -it -p 5000:5000 --name cat codeandtalk /bin/bash
ENV LC_ALL      C.UTF-8
ENV LANG        C.UTF-8
ENV PYTHONPATH  /opt

#   export LC_ALL=C.UTF-8
#   export LANG=C.UTF-8
#   export PYTHONPATH=/opt
#   FLASK_APP=cat.app FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5000


# docker start cat && docker attach cat

EXPOSE 5000
 
# ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--module", "app:app", "--processes", "1", "--threads", "8"]
