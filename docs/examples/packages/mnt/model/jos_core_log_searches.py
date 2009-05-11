# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_core_log_searches',  pkey='None',name_long='jos_core_log_searches')
        tbl.column('search_term', dtype ='A', notnull ='y', size ='0:128', name_long ='!!Search_Term')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
