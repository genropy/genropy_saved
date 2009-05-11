# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_rooms',  pkey='id',name_long='jos_fc_rooms')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('updated', dtype ='DH', name_long ='!!Updated', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:64', name_long ='!!Name')  
        tbl.column('password', dtype ='A', notnull ='y', size ='0:32', name_long ='!!Password')  
        tbl.column('ispublic', dtype ='A', name_long ='!!Ispublic', size ='1')  
        tbl.column('ispermanent', dtype ='I', name_long ='!!Ispermanent')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
