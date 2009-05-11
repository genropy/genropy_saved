# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_msg',  pkey='id',name_long='jos_community_msg')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('from', dtype ='I', name_long ='!!From', notnull ='y')  
        tbl.column('parent', dtype ='I', name_long ='!!Parent', notnull ='y')  
        tbl.column('deleted', dtype ='I', name_long ='!!Deleted')  
        tbl.column('from_name', size ='0:45', dtype ='A', name_long ='!!From_Name', notnull ='y')  
        tbl.column('posted_on', dtype ='DH', name_long ='!!Posted_On')  
        tbl.column('subject', dtype ='T', name_long ='!!Subject', notnull ='y')  
        tbl.column('body', dtype ='T', name_long ='!!Body', notnull ='y')  
