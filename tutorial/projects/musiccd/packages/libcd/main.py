#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Libreria cd', sqlschema='libcd',
                    name_short='cd', name_long='Libreria cd rom', name_full='Cd fighissimo')

    def config_db(self, pkg):
        pass

        #def loginUrl(self):
        #    return 'base/login'
        #

class Table(GnrDboTable):
    pass
    
    