# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_log_items',  pkey='None',name_long='jos_core_log_items')
        tbl.column('time_stamp', dtype ='D', name_long ='!!Time_Stamp', notnull ='y')  
        tbl.column('item_table', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Item_Table')  
        tbl.column('item_id', dtype ='I', name_long ='!!Item_Id', notnull ='y')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
