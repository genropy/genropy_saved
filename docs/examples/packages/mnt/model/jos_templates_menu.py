# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_templates_menu',  pkey='None',name_long='jos_templates_menu')
        tbl.column('template', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Template')  
        tbl.column('menuid', dtype ='I', name_long ='!!Menuid', notnull ='y')  
        tbl.column('client_id', dtype ='I', name_long ='!!Client_Id', notnull ='y')  
