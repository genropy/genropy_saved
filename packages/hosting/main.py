
#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='hosting package',sqlschema='hosting',
                name_short='Hosting', name_long='Hosting', name_full='Hosting')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'hosting/login'

class Table(GnrDboTable):
    pass
