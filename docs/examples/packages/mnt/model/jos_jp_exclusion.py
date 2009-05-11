# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jp_exclusion',  pkey='id',name_long='jos_jp_exclusion')
        tbl.column('id', dtype ='L', name_long ='!!Id', notnull ='y')  
        tbl.column('profile', dtype ='I', name_long ='!!Profile', notnull ='y')  
        tbl.column('class', size ='0:255', dtype ='A', name_long ='!!Class', notnull ='y')  
        tbl.column('value', dtype ='T', name_long ='!!Value', notnull ='y')  
