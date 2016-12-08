#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import metadata
class Table(object):


    @metadata(mandatory=True)
    def sysRecord_ORGN(self):
        return self.newrecord(code='ORGN',description='Organizer',isreserved=True,note='ORGN ENABLED')