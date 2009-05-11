# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_activities',  pkey='id',name_long='jos_community_activities')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('actor', dtype ='I', name_long ='!!Actor', notnull ='y')  
        tbl.column('target', dtype ='I', name_long ='!!Target', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title')  
        tbl.column('content', dtype ='T', name_long ='!!Content', notnull ='y')  
        tbl.column('app', size ='0:200', dtype ='A', name_long ='!!App', notnull ='y')  
        tbl.column('cid', dtype ='I', name_long ='!!Cid', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
        tbl.column('points', dtype ='I', name_long ='!!Points', notnull ='y')  
        tbl.column('archived', dtype ='I', name_long ='!!Archived', notnull ='y')  
