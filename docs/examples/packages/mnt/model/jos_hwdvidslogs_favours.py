# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdvidslogs_favours',  pkey='id',name_long='jos_hwdvidslogs_favours')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('videoid', dtype ='I', name_long ='!!Videoid', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('favour', dtype ='I', name_long ='!!Favour', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
