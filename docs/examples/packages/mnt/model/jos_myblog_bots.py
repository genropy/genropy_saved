# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_bots',  pkey='id',name_long='jos_myblog_bots')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='T', name_long ='!!Name', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
        tbl.column('filename', dtype ='T', name_long ='!!Filename', notnull ='y')  
        tbl.column('folder', dtype ='T', name_long ='!!Folder', notnull ='y')  
