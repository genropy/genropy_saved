# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_acl_aro',  pkey='id',name_long='jos_core_acl_aro')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('section_value', dtype ='A', notnull ='y', size ='0:240', name_long ='!!Section_Value')  
        tbl.column('value', dtype ='A', notnull ='y', size ='0:240', name_long ='!!Value')  
        tbl.column('order_value', dtype ='I', name_long ='!!Order_Value', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('hidden', dtype ='I', name_long ='!!Hidden', notnull ='y')  
