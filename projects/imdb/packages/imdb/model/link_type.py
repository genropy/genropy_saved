# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('link_type', pkey='id', name_long='link_type')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('link', _childname ='columns.link', dtype ='A', notnull ='y', size ='0:32', name_long ='!!Link')  
