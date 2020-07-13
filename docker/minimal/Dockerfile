FROM alpine:latest AS builder
MAINTAINER Tamas Nepusz <ntamas@gmail.com>
LABEL Description="Simple Docker image that contains a pre-compiled version of igraph's Python interface"

RUN apk add --no-cache --update \
  make gcc g++ libstdc++ git python3-dev libxslt-dev libxml2-dev libc-dev \
  libffi-dev zlib-dev py-pip libxml2 zlib libtool autoconf automake \
  flex bison \
  && rm -rf /var/cache/apk/*

RUN pip3 install git+https://github.com/igraph/python-igraph
RUN pip3 install cairocffi

FROM alpine:latest

RUN apk add --no-cache --update \
  python3 libstdc++ libxml2 libxslt zlib cairo \
  && rm -rf /var/cache/apk/*

COPY --from=builder /usr/lib/python3.7/site-packages/cairocffi /usr/lib/python3.7/site-packages/cairocffi
COPY --from=builder /usr/lib/python3.7/site-packages/igraph /usr/lib/python3.7/site-packages/igraph
COPY --from=builder /usr/bin/igraph /usr/bin

CMD /usr/bin/igraph

