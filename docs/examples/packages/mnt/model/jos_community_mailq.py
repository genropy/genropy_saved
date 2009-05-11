# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_mailq',  pkey='id',name_long='jos_community_mailq')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('recipient', dtype ='T', name_long ='!!Recipient', notnull ='y')  
        tbl.column('subject', dtype ='T', name_long ='!!Subject', notnull ='y')  
        tbl.column('body', dtype ='T', name_long ='!!Body', notnull ='y')  
        tbl.column('status', dtype ='I', name_long ='!!Status', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
