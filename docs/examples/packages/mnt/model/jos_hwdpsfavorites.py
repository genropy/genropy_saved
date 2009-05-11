# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpsfavorites',  pkey='id',name_long='jos_hwdpsfavorites')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('photoid', dtype ='I', name_long ='!!Photoid')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
