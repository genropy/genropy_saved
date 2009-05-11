# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_modules',  pkey='id',name_long='jos_modules')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title', notnull ='y')  
        tbl.column('content', dtype ='T', name_long ='!!Content', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('position', dtype ='A', name_long ='!!Position', size ='0:50')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('module', dtype ='A', name_long ='!!Module', size ='0:50')  
        tbl.column('numnews', dtype ='I', name_long ='!!Numnews', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('showtitle', dtype ='I', name_long ='!!Showtitle', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
        tbl.column('iscore', dtype ='I', name_long ='!!Iscore', notnull ='y')  
        tbl.column('client_id', dtype ='I', name_long ='!!Client_Id', notnull ='y')  
        tbl.column('control', dtype ='T', name_long ='!!Control', notnull ='y')  
