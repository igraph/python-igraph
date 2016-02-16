FROM ubuntu:latest
MAINTAINER Tamas Nepusz <ntamas@gmail.com>
LABEL Description="Simple Docker image that contains a pre-compiled version of igraph's Python interface"
RUN apt-get -y update && apt-get -y install build-essential libxml2-dev zlib1g-dev python-dev python-pip pkg-config libffi-dev libcairo-dev
RUN pip install python-igraph
RUN pip install cairocffi
CMD /usr/local/bin/igraph
