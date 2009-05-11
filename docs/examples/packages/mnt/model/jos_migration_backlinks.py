# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_migration_backlinks',  pkey='itemid',name_long='jos_migration_backlinks')
        tbl.column('itemid', dtype ='I', name_long ='!!Itemid', notnull ='y')  
        tbl.column('name', size ='0:100', dtype ='A', name_long ='!!Name', notnull ='y')  
        tbl.column('url', dtype ='T', name_long ='!!Url', notnull ='y')  
        tbl.column('sefurl', dtype ='T', name_long ='!!Sefurl', notnull ='y')  
        tbl.column('newurl', dtype ='T', name_long ='!!Newurl', notnull ='y')  
