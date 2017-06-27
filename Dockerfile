FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
WORKDIR /webapp
COPY requirements.txt /webapp/
#RUN pip install -r /webapp/requirements.txt
#ENTRYPOINT ["python"]
#CMD ["app.py"]

# docker build -t codeandtalk .

# docker run -v $(pwd):/opt -it --name cat codeandtalk /bin/bash
