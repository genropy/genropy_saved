
#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='showcase15 package',sqlschema='showcase15',
                name_short='Showcase15', name_long='Showcase15', name_full='Showcase15')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'showcase15/login'

class Table(GnrDboTable):
    pass
