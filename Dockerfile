FROM ubuntu
MAINTAINER Alex Young
RUN apt-get update
RUN apt-get install -y python python-dev python-distribute python-pip
RUN pip install Flask
EXPOSE 80
ADD dist /dist
WORKDIR /dist
CMD sudo python ttt.py -d
