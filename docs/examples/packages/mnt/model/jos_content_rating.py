# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_content_rating',  pkey='content_id',name_long='jos_content_rating')
        tbl.column('content_id', dtype ='I', name_long ='!!Content_Id', notnull ='y')  
        tbl.column('rating_sum', dtype ='I', name_long ='!!Rating_Sum', notnull ='y')  
        tbl.column('rating_count', dtype ='I', name_long ='!!Rating_Count', notnull ='y')  
        tbl.column('lastip', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Lastip')  
