############################################################
# Dockerfile to build Genropy container images
# Based on Ubuntu
############################################################

FROM alpine:3.7
MAINTAINER Francesco Porcari - francesco@genropy.org

RUN apk update
RUN apk add git
RUN apk add python3
RUN apk add py3-lxml
RUN apk add py3-psutil
RUN apk add supervisor 
RUN apk add nginx 

ADD . /home/genropy
RUN pip3 install paver
WORKDIR /home/genropy/gnrpy
RUN paver develop
RUN python3 initgenropy.py
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf



