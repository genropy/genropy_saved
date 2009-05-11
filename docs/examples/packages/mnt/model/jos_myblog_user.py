# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_user',  pkey='user_id',name_long='jos_myblog_user')
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title', notnull ='y')  
        tbl.column('feedburner', dtype ='T', name_long ='!!Feedburner', notnull ='y')  
        tbl.column('style', dtype ='T', name_long ='!!Style', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
