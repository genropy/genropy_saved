# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_groups_category',  pkey='id',name_long='jos_community_groups_category')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', size ='0:255', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
