# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_photos',  pkey='id',name_long='jos_community_photos')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('albumid', dtype ='I', name_long ='!!Albumid', notnull ='y')  
        tbl.column('caption', dtype ='T', name_long ='!!Caption', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('creator', dtype ='I', name_long ='!!Creator', notnull ='y')  
        tbl.column('permissions', size ='0:255', dtype ='A', name_long ='!!Permissions', notnull ='y')  
        tbl.column('image', size ='0:255', dtype ='A', name_long ='!!Image', notnull ='y')  
        tbl.column('thumbnail', size ='0:255', dtype ='A', name_long ='!!Thumbnail', notnull ='y')  
        tbl.column('original', size ='0:255', dtype ='A', name_long ='!!Original', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
