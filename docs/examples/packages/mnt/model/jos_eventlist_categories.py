# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_eventlist_categories',  pkey='id',name_long='jos_eventlist_categories')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('parent_id', dtype ='I', name_long ='!!Parent_Id', notnull ='y')  
        tbl.column('catname', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Catname')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Alias')  
        tbl.column('catdescription', dtype ='T', name_long ='!!Catdescription', notnull ='y')  
        tbl.column('meta_keywords', dtype ='T', name_long ='!!Meta_Keywords', notnull ='y')  
        tbl.column('meta_description', dtype ='T', name_long ='!!Meta_Description', notnull ='y')  
        tbl.column('image', dtype ='A', notnull ='y', size ='0:100', name_long ='!!Image')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('access', dtype ='I', name_long ='!!Access', notnull ='y')  
        tbl.column('groupid', dtype ='I', name_long ='!!Groupid', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
