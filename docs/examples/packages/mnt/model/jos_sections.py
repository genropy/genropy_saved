# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_sections',  pkey='id',name_long='jos_sections')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('image', dtype ='T', name_long ='!!Image', notnull ='y')  
        tbl.column('scope', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Scope')  
        tbl.column('image_position', dtype ='A', notnull ='y', size ='0:30', name_long ='!!Image_Position')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('count', dtype ='I', name_long ='!!Count', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
