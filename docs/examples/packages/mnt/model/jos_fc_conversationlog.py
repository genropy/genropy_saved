# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_conversationlog',  pkey='id',name_long='jos_fc_conversationlog')
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('input', dtype ='T', name_long ='!!Input')  
        tbl.column('response', dtype ='T', name_long ='!!Response')  
        tbl.column('uid', dtype ='A', name_long ='!!Uid', size ='0:255')  
        tbl.column('enteredtime', dtype ='DH', name_long ='!!Enteredtime', notnull ='y')  
