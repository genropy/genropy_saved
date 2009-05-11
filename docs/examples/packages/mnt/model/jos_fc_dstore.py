# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_dstore',  pkey='id',name_long='jos_fc_dstore')
        tbl.column('uid', dtype ='A', name_long ='!!Uid', size ='0:255')  
        tbl.column('name', dtype ='T', name_long ='!!Name')  
        tbl.column('value', dtype ='T', name_long ='!!Value')  
        tbl.column('enteredtime', dtype ='DH', name_long ='!!Enteredtime', notnull ='y')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
