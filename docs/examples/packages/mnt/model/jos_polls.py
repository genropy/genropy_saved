# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_polls',  pkey='id',name_long='jos_polls')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('voters', dtype ='I', name_long ='!!Voters', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('lag', dtype ='I', name_long ='!!Lag', notnull ='y')  
