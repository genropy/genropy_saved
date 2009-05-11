# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_groups_bulletins',  pkey='id',name_long='jos_community_groups_bulletins')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid', notnull ='y')  
        tbl.column('created_by', dtype ='I', name_long ='!!Created_By', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('title', size ='0:255', dtype ='A', name_long ='!!Title', notnull ='y')  
        tbl.column('message', dtype ='T', name_long ='!!Message', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
