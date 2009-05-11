# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_menu_types',  pkey='id',name_long='jos_menu_types')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('menutype', dtype ='A', notnull ='y', size ='0:75', name_long ='!!Menutype')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('description', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Description')  
