# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_config',  pkey='None',name_long='jos_community_config')
        tbl.column('name', size ='0:64', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
