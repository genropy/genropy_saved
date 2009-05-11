# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdvidsgs',  pkey='id',name_long='jos_hwdvidsgs')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('setting', dtype ='A', name_long ='!!Setting', size ='0:250')  
        tbl.column('value', dtype ='T', name_long ='!!Value')  
