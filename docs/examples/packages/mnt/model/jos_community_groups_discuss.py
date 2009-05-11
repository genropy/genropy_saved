# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_groups_discuss',  pkey='id',name_long='jos_community_groups_discuss')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('parentid', dtype ='I', name_long ='!!Parentid', notnull ='y')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid', notnull ='y')  
        tbl.column('creator', dtype ='I', name_long ='!!Creator', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title', notnull ='y')  
        tbl.column('message', dtype ='T', name_long ='!!Message', notnull ='y')  
