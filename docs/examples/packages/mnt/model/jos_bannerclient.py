# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_bannerclient',  pkey='cid',name_long='jos_bannerclient')
        tbl.column('cid', dtype ='I', name_long ='!!Cid', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('contact', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Contact')  
        tbl.column('email', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Email')  
        tbl.column('extrainfo', dtype ='T', name_long ='!!Extrainfo', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='H', name_long ='!!Checked_Out_Time')  
        tbl.column('editor', dtype ='A', name_long ='!!Editor', size ='0:50')  
