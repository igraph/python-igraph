FROM python:latest
MAINTAINER Tamas Nepusz <ntamas@gmail.com>
LABEL Description="Simple Docker image that contains a pre-compiled version of igraph's Python interface"

RUN pip3 install igraph cairocffi

CMD /usr/local/bin/igraph

