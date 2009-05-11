# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_acl_aro_groups',  pkey='id',name_long='jos_core_acl_aro_groups')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('parent_id', dtype ='I', name_long ='!!Parent_Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('lft', dtype ='I', name_long ='!!Lft', notnull ='y')  
        tbl.column('rgt', dtype ='I', name_long ='!!Rgt', notnull ='y')  
        tbl.column('value', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Value')  
