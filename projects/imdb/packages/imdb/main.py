#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='imdb package',sqlprefix='', sqlscheme='imdb',#if omitted it means 'public'
                    name_short='Imdb', name_long='Imdb', name_full='Imdb')
                    
    def config_db(self, pkg):
        pass
        
    # def loginUrl(self):
    #     return 'imdb/login'
        
class Table(GnrDboTable):
    pass
