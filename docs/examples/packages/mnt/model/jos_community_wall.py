# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_wall',  pkey='id',name_long='jos_community_wall')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('post_by', dtype ='I', name_long ='!!Post_By', notnull ='y')  
        tbl.column('ip', size ='0:45', dtype ='A', name_long ='!!Ip', notnull ='y')  
        tbl.column('comment', dtype ='T', name_long ='!!Comment', notnull ='y')  
        tbl.column('date', size ='0:45', dtype ='A', name_long ='!!Date', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('type', size ='0:200', dtype ='A', name_long ='!!Type', notnull ='y')  
