#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import Table_userobject

class Package(object):
    def config_attributes(self):
        return dict(comment='devlang package',sqlschema='devlang',
                name_short='Devlang', name_long='Developers languages', name_full='Demo: Developers languages')
