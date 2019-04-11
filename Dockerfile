############################################################
# Dockerfile to build Genropy container images
# Based on Ubuntu
############################################################

FROM genropy/ubuntu-python
MAINTAINER Francesco Porcari - francesco@genropy.org

ADD . /home/genropy

RUN apt-get update
RUN apt-get install -y supervisor nginx liblzma-dev
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
RUN easy_install pip
RUN pip install gunicorn gevent futures
RUN pip install 'Tornado>=4.0.0,<5.0.0'
RUN mkdir -p /var/log/supervisor
WORKDIR /home/genropy/gnrpy
RUN paver develop
RUN python initgenropy.py


ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf




