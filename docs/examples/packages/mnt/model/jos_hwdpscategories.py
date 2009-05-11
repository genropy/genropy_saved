# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpscategories',  pkey='id',name_long='jos_hwdpscategories')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('parent', dtype ='I', name_long ='!!Parent', notnull ='y')  
        tbl.column('category_name', dtype ='A', name_long ='!!Category_Name', size ='0:250')  
        tbl.column('category_description', dtype ='T', name_long ='!!Category_Description')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('access_b_v', dtype ='I', name_long ='!!Access_B_V', notnull ='y')  
        tbl.column('access_u_r', dtype ='A', notnull ='y', size ='0:7', name_long ='!!Access_U_R')  
        tbl.column('access_v_r', dtype ='A', notnull ='y', size ='0:7', name_long ='!!Access_V_R')  
        tbl.column('access_u', dtype ='I', name_long ='!!Access_U', notnull ='y')  
        tbl.column('access_lev_u', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Access_Lev_U')  
        tbl.column('access_v', dtype ='I', name_long ='!!Access_V', notnull ='y')  
        tbl.column('access_lev_v', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Access_Lev_V')  
        tbl.column('num_albums', dtype ='I', name_long ='!!Num_Albums', notnull ='y')  
        tbl.column('num_subcats', dtype ='I', name_long ='!!Num_Subcats', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
