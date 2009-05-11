# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_components',  pkey='id',name_long='jos_components')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Name')  
        tbl.column('link', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Link')  
        tbl.column('menuid', dtype ='I', name_long ='!!Menuid', notnull ='y')  
        tbl.column('parent', dtype ='I', name_long ='!!Parent', notnull ='y')  
        tbl.column('admin_menu_link', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Admin_Menu_Link')  
        tbl.column('admin_menu_alt', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Admin_Menu_Alt')  
        tbl.column('option', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Option')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('admin_menu_img', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Admin_Menu_Img')  
        tbl.column('iscore', dtype ='I', name_long ='!!Iscore', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
        tbl.column('enabled', dtype ='I', name_long ='!!Enabled', notnull ='y')  
