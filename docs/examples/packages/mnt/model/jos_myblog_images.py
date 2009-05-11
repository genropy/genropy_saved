# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_images',  pkey='id',name_long='jos_myblog_images')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('filename', dtype ='T', name_long ='!!Filename', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id', notnull ='y')  
