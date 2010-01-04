
#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='base package',sqlschema='base',
                name_short='Base', name_long='Base', name_full='Base')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'prj/login'

class Table(GnrDboTable):
    pass
