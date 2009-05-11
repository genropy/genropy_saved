# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_uploads',  pkey='id',name_long='jos_myblog_uploads')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('path', dtype ='T', name_long ='!!Path', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('approved', dtype ='I', name_long ='!!Approved', notnull ='y')  
        tbl.column('caption', dtype ='T', name_long ='!!Caption', notnull ='y')  
