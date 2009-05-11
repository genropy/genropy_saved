# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_groups_members',  pkey='None',name_long='jos_community_groups_members')
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid', notnull ='y')  
        tbl.column('memberid', dtype ='I', name_long ='!!Memberid', notnull ='y')  
        tbl.column('approved', dtype ='I', name_long ='!!Approved', notnull ='y')  
        tbl.column('permissions', size ='0:255', dtype ='A', name_long ='!!Permissions', notnull ='y')  
