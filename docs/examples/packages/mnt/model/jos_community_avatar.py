# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_avatar',  pkey='None',name_long='jos_community_avatar')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('apptype', size ='0:255', dtype ='A', name_long ='!!Apptype', notnull ='y')  
        tbl.column('path', dtype ='T', name_long ='!!Path', notnull ='y')  
        tbl.column('type', dtype ='I', name_long ='!!Type', notnull ='y')  
