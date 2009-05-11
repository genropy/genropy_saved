# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdvidsgroup_membership',  pkey='id',name_long='jos_hwdvidsgroup_membership')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('memberid', dtype ='I', name_long ='!!Memberid')  
        tbl.column('memberusername', dtype ='A', name_long ='!!Memberusername', size ='0:250')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('groupadmin', dtype ='A', name_long ='!!Groupadmin', size ='0:250')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid')  
        tbl.column('approved', dtype ='I', name_long ='!!Approved', notnull ='y')  
