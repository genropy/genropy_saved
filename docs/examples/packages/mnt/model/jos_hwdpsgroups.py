# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpsgroups',  pkey='id',name_long='jos_hwdpsgroups')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('group_name', dtype ='T', name_long ='!!Group_Name')  
        tbl.column('privacy', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Privacy')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('allow_comments', dtype ='I', name_long ='!!Allow_Comments', notnull ='y')  
        tbl.column('require_approval', dtype ='I', name_long ='!!Require_Approval', notnull ='y')  
        tbl.column('group_description', dtype ='T', name_long ='!!Group_Description')  
        tbl.column('featured', dtype ='I', name_long ='!!Featured', notnull ='y')  
        tbl.column('adminid', dtype ='I', name_long ='!!Adminid')  
        tbl.column('total_members', dtype ='I', name_long ='!!Total_Members')  
        tbl.column('total_photos', dtype ='I', name_long ='!!Total_Photos')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
