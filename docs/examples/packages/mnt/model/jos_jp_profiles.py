# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jp_profiles',  pkey='id',name_long='jos_jp_profiles')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('description', size ='0:255', dtype ='A', name_long ='!!Description', notnull ='y')  
