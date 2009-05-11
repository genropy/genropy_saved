# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpsrating',  pkey='id',name_long='jos_hwdpsrating')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('photoid', dtype ='I', name_long ='!!Photoid')  
        tbl.column('ip', dtype ='A', notnull ='y', size ='0:15', name_long ='!!Ip')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
