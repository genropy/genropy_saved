# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_config_values',  pkey='id',name_long='jos_fc_config_values')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id', notnull ='y')  
        tbl.column('config_id', dtype ='I', name_long ='!!Config_Id', notnull ='y')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
        tbl.column('disabled', dtype ='I', name_long ='!!Disabled', notnull ='y')  
