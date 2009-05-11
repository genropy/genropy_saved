# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_content_frontpage',  pkey='content_id',name_long='jos_content_frontpage')
        tbl.column('content_id', dtype ='I', name_long ='!!Content_Id', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
