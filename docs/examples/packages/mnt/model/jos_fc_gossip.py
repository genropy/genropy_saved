# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_gossip',  pkey='id',name_long='jos_fc_gossip')
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('gossip', dtype ='T', name_long ='!!Gossip')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
