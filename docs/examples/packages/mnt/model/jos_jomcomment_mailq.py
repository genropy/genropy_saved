# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_mailq',  pkey='id',name_long='jos_jomcomment_mailq')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('email', size ='0:200', dtype ='A', name_long ='!!Email', notnull ='y')  
        tbl.column('status', dtype ='I', name_long ='!!Status', notnull ='y')  
        tbl.column('title', size ='0:200', dtype ='A', name_long ='!!Title', notnull ='y')  
        tbl.column('name', size ='0:200', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('content', dtype ='T', name_long ='!!Content', notnull ='y')  
        tbl.column('posted_on', dtype ='DH', name_long ='!!Posted_On', notnull ='y')  
        tbl.column('commentid', dtype ='I', name_long ='!!Commentid', notnull ='y')  
