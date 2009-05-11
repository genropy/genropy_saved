# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_config',  pkey='id',name_long='jos_fc_config')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('level_0', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Level_0')  
        tbl.column('level_1', dtype ='A', name_long ='!!Level_1', size ='0:255')  
        tbl.column('level_2', dtype ='A', name_long ='!!Level_2', size ='0:255')  
        tbl.column('level_3', dtype ='A', name_long ='!!Level_3', size ='0:255')  
        tbl.column('level_4', dtype ='A', name_long ='!!Level_4', size ='0:255')  
        tbl.column('type', dtype ='A', name_long ='!!Type', size ='0:10')  
        tbl.column('units', dtype ='A', notnull ='y', size ='0:10', name_long ='!!Units')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('comment', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Comment')  
        tbl.column('info', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Info')  
        tbl.column('parent_page', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Parent_Page')  
        tbl.column('_order', dtype ='I', name_long ='!!_Order', notnull ='y')  
