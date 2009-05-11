# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_poll_menu',  pkey='None',name_long='jos_poll_menu')
        tbl.column('pollid', dtype ='I', name_long ='!!Pollid', notnull ='y')  
        tbl.column('menuid', dtype ='I', name_long ='!!Menuid', notnull ='y')  
