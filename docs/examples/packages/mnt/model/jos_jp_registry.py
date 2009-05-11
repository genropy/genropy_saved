# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jp_registry',  pkey='id',name_long='jos_jp_registry')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('profile', dtype ='I', name_long ='!!Profile', notnull ='y')  
        tbl.column('key', size ='0:255', dtype ='A', name_long ='!!Key', notnull ='y')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
