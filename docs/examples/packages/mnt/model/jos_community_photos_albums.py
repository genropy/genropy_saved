# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_photos_albums',  pkey='id',name_long='jos_community_photos_albums')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('photoid', dtype ='I', name_long ='!!Photoid', notnull ='y')  
        tbl.column('creator', dtype ='I', name_long ='!!Creator', notnull ='y')  
        tbl.column('name', size ='0:255', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('permissions', size ='0:255', dtype ='A', name_long ='!!Permissions', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
