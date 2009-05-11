# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_gmcache',  pkey='id',name_long='jos_fc_gmcache')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('template', dtype ='I', name_long ='!!Template', notnull ='y')  
        tbl.column('inputstarvals', dtype ='T', name_long ='!!Inputstarvals')  
        tbl.column('thatstarvals', dtype ='T', name_long ='!!Thatstarvals')  
        tbl.column('topicstarvals', dtype ='T', name_long ='!!Topicstarvals')  
        tbl.column('patternmatched', dtype ='T', name_long ='!!Patternmatched')  
        tbl.column('inputmatched', dtype ='T', name_long ='!!Inputmatched')  
        tbl.column('combined', dtype ='T', name_long ='!!Combined', notnull ='y')  
