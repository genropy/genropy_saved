# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_templates',  pkey='id',name_long='jos_fc_templates')
        tbl.column('bot', dtype ='I', name_long ='!!Bot', notnull ='y')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('template', dtype ='T', name_long ='!!Template', notnull ='y')  
        tbl.column('pattern', dtype ='A', name_long ='!!Pattern', size ='0:255')  
        tbl.column('that', dtype ='A', name_long ='!!That', size ='0:255')  
        tbl.column('topic', dtype ='A', name_long ='!!Topic', size ='0:255')  
