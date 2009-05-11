# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_reports',  pkey='id',name_long='jos_jomcomment_reports')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('ip', size ='0:24', dtype ='A', name_long ='!!Ip', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
        tbl.column('commentid', dtype ='I', name_long ='!!Commentid', notnull ='y')  
        tbl.column('option', size ='0:128', dtype ='A', name_long ='!!Option', notnull ='y')  
        tbl.column('reason', dtype ='T', name_long ='!!Reason', notnull ='y')  
        tbl.column('status', dtype ='I', name_long ='!!Status', notnull ='y')  
