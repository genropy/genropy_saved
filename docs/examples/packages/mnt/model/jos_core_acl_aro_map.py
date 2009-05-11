# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_acl_aro_map',  pkey='None',name_long='jos_core_acl_aro_map')
        tbl.column('acl_id', dtype ='I', name_long ='!!Acl_Id', notnull ='y')  
        tbl.column('section_value', dtype ='A', notnull ='y', size ='0:230', name_long ='!!Section_Value')  
        tbl.column('value', size ='0:100', dtype ='A', name_long ='!!Value', notnull ='y')  
