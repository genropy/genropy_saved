############################################################
# Dockerfile to build Genropy container images
# Based on Ubuntu
############################################################

FROM genropy/ubuntu-python
MAINTAINER Francesco Porcari - francesco@genropy.org

ADD . /home/genropy
WORKDIR /home/genropy/gnrpy
RUN paver develop
RUN python initgenropy.py

RUN apt-get update
RUN apt-get install -y supervisor nginx
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
RUN easy_install pip
RUN pip install gunicorn gevent 
RUN pip install 'Tornado>=4.0.0,<5.0.0'
RUN mkdir -p /var/log/supervisor

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf




