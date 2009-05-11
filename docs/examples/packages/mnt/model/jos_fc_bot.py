# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_bot',  pkey='id',name_long='jos_fc_bot')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
