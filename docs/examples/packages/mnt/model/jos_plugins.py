# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_plugins',  pkey='id',name_long='jos_plugins')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Name')  
        tbl.column('element', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Element')  
        tbl.column('folder', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Folder')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('iscore', dtype ='I', name_long ='!!Iscore', notnull ='y')  
        tbl.column('client_id', dtype ='I', name_long ='!!Client_Id', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
