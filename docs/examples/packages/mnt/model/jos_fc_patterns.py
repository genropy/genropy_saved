# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_patterns',  pkey='id',name_long='jos_fc_patterns')
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('word', dtype ='A', name_long ='!!Word', size ='0:255')  
        tbl.column('ordera', dtype ='I', name_long ='!!Ordera', notnull ='y')  
        tbl.column('parent', dtype ='I', name_long ='!!Parent', notnull ='y')  
        tbl.column('isend', dtype ='I', name_long ='!!Isend', notnull ='y')  
