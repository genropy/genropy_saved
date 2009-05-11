# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_content_categories',  pkey='id',name_long='jos_myblog_content_categories')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('category', dtype ='I', name_long ='!!Category', notnull ='y')  
