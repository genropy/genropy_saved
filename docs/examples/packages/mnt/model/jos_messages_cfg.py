# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_messages_cfg',  pkey='None',name_long='jos_messages_cfg')
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
        tbl.column('cfg_name', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Cfg_Name')  
        tbl.column('cfg_value', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Cfg_Value')  
