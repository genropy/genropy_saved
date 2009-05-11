# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_config_chats',  pkey='id',name_long='jos_fc_config_chats')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='100', name_long ='!!Name')  
        tbl.column('instances', dtype ='A', notnull ='y', size ='255', name_long ='!!Instances')  
        tbl.column('is_default', dtype ='I', name_long ='!!Is_Default', notnull ='y')  
