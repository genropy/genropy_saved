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



