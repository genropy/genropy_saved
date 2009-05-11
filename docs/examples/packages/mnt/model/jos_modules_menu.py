# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_modules_menu',  pkey='None',name_long='jos_modules_menu')
        tbl.column('moduleid', dtype ='I', name_long ='!!Moduleid', notnull ='y')  
        tbl.column('menuid', dtype ='I', name_long ='!!Menuid', notnull ='y')  
