# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_newsfeeds',  pkey='id',name_long='jos_newsfeeds')
        tbl.column('catid', dtype ='I', name_long ='!!Catid', notnull ='y')  
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('name', dtype ='T', name_long ='!!Name', notnull ='y')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('link', dtype ='T', name_long ='!!Link', notnull ='y')  
        tbl.column('filename', dtype ='A', name_long ='!!Filename', size ='0:200')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('numarticles', dtype ='I', name_long ='!!Numarticles', notnull ='y')  
        tbl.column('cache_time', dtype ='I', name_long ='!!Cache_Time', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('rtl', dtype ='I', name_long ='!!Rtl', notnull ='y')  
