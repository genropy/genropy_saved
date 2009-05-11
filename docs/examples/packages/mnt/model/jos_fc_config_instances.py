# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_config_instances',  pkey='id',name_long='jos_fc_config_instances')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('is_active', dtype ='I', name_long ='!!Is_Active', notnull ='y')  
        tbl.column('is_default', dtype ='I', name_long ='!!Is_Default', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Name')  
        tbl.column('created_date', dtype ='DH', name_long ='!!Created_Date', notnull ='y')  
