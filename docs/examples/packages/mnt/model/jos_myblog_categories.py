# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_categories',  pkey='id',name_long='jos_myblog_categories')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Name')  
        tbl.column('default', dtype ='A', notnull ='y', size ='0:5', name_long ='!!Default')  
        tbl.column('slug', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Slug')  
