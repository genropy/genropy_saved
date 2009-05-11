# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_stats_agents',  pkey='None',name_long='jos_stats_agents')
        tbl.column('agent', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Agent')  
        tbl.column('type', dtype ='I', name_long ='!!Type', notnull ='y')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
