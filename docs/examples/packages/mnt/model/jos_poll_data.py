# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_poll_data',  pkey='id',name_long='jos_poll_data')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('pollid', dtype ='I', name_long ='!!Pollid', notnull ='y')  
        tbl.column('text', dtype ='T', name_long ='!!Text', notnull ='y')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
