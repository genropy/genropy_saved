#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Deploy package', sqlschema='deploy',
                    name_short='Deploy', name_long='Deploy', name_full='Deploy')

class Table(GnrDboTable):
    pass
