#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='docu package',sqlschema='docu',sqlprefix=True,
                    name_short='Docu', name_long='Documentation', name_full='Docu')
                    
    def htmlProcessorName(self):
        return '/docu/index/rst'

    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass
