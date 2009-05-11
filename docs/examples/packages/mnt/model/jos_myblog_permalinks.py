# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_permalinks',  pkey='contentid',name_long='jos_myblog_permalinks')
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('permalink', dtype ='T', name_long ='!!Permalink', notnull ='y')  
