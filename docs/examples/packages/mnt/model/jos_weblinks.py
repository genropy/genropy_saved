# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_weblinks',  pkey='id',name_long='jos_weblinks')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('catid', dtype ='I', name_long ='!!Catid', notnull ='y')  
        tbl.column('sid', dtype ='I', name_long ='!!Sid', notnull ='y')  
        tbl.column('title', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Title')  
        tbl.column('alias', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Alias')  
        tbl.column('url', dtype ='A', notnull ='y', size ='0:250', name_long ='!!Url')  
        tbl.column('description', dtype ='T', name_long ='!!Description', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('hits', dtype ='I', name_long ='!!Hits', notnull ='y')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('checked_out', dtype ='I', name_long ='!!Checked_Out', notnull ='y')  
        tbl.column('checked_out_time', dtype ='DH', name_long ='!!Checked_Out_Time', notnull ='y')  
        tbl.column('ordering', dtype ='I', name_long ='!!Ordering', notnull ='y')  
        tbl.column('archived', dtype ='I', name_long ='!!Archived', notnull ='y')  
        tbl.column('approved', dtype ='I', name_long ='!!Approved', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
