# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_bots',  pkey='botname',name_long='jos_fc_bots')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('botname', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Botname')  
