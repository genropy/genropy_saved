# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_categories',  pkey='id',name_long='jos_categories')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('parent_id', dtype ='I', name_long ='!!Parent_Id', notnull ='y')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Title')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Name')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('image', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Image')  
        tbl.column('section', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Section')  
        tbl.column('image_position', dtype ='A', notnull ='y', size ='0:30', name_long ='!!Image_Position')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('editor', dtype ='A', name_long ='!!Editor', size ='0:50')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('count', dtype ='I', name_long ='!!Count', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
