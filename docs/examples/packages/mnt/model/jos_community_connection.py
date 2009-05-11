# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_connection',  pkey='connection_id',name_long='jos_community_connection')
        tbl.column('connection_id', dtype ='I', name_long ='!!Connection_Id', notnull ='y')  
        tbl.column('connect_from', dtype ='I', name_long ='!!Connect_From', notnull ='y')  
        tbl.column('connect_to', dtype ='I', name_long ='!!Connect_To', notnull ='y')  
        tbl.column('status', dtype ='I', name_long ='!!Status', notnull ='y')  
        tbl.column('group', dtype ='I', name_long ='!!Group', notnull ='y')  
