# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_files',  pkey='id',name_long='jos_community_files')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('creator', dtype ='I', name_long ='!!Creator', notnull ='y')  
        tbl.column('name', dtype ='T', name_long ='!!Name', notnull ='y')  
        tbl.column('caption', dtype ='T', name_long ='!!Caption', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('permissions', size ='0:255', dtype ='A', name_long ='!!Permissions', notnull ='y')  
        tbl.column('thumbnail', size ='0:255', dtype ='A', name_long ='!!Thumbnail', notnull ='y')  
        tbl.column('source', size ='0:255', dtype ='A', name_long ='!!Source', notnull ='y')  
        tbl.column('type', size ='0:255', dtype ='A', name_long ='!!Type', notnull ='y')  
