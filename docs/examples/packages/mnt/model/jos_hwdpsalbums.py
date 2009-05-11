# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpsalbums',  pkey='id',name_long='jos_hwdpsalbums')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title')  
        tbl.column('description', dtype ='T', name_long ='!!Description')  
        tbl.column('tags', dtype ='T', name_long ='!!Tags')  
        tbl.column('category_id', dtype ='I', name_long ='!!Category_Id')  
        tbl.column('date_created', dtype ='DH', name_long ='!!Date_Created', notnull ='y')  
        tbl.column('date_modified', dtype ='DH', name_long ='!!Date_Modified', notnull ='y')  
        tbl.column('location', dtype ='T', name_long ='!!Location')  
        tbl.column('allow_comments', dtype ='I', name_long ='!!Allow_Comments', notnull ='y')  
        tbl.column('allow_ratings', dtype ='I', name_long ='!!Allow_Ratings', notnull ='y')  
        tbl.column('privacy', dtype ='A', name_long ='!!Privacy', size ='0:250')  
        tbl.column('approved', dtype ='A', name_long ='!!Approved', size ='0:250')  
        tbl.column('user_id', dtype ='I', name_long ='!!User_Id')  
        tbl.column('number_of_photos', dtype ='I', name_long ='!!Number_Of_Photos')  
        tbl.column('featured', dtype ='I', name_long ='!!Featured', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
