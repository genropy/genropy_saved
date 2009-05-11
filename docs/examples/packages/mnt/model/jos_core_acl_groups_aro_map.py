# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_acl_groups_aro_map',  pkey='None',name_long='jos_core_acl_groups_aro_map')
        tbl.column('group_id', dtype ='I', name_long ='!!Group_Id', notnull ='y')  
        tbl.column('section_value', dtype ='A', notnull ='y', size ='0:240', name_long ='!!Section_Value')  
        tbl.column('aro_id', dtype ='I', name_long ='!!Aro_Id', notnull ='y')  
