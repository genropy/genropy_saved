# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_tb',  pkey='id',name_long='jos_jomcomment_tb')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('ip', dtype ='A', notnull ='y', size ='0:18', name_long ='!!Ip')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('title', dtype ='T', name_long ='!!Title', notnull ='y')  
        tbl.column('excerpt', dtype ='T', name_long ='!!Excerpt', notnull ='y')  
        tbl.column('url', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Url')  
        tbl.column('blog_name', dtype ='T', name_long ='!!Blog_Name', notnull ='y')  
        tbl.column('charset', dtype ='A', notnull ='y', size ='0:45', name_long ='!!Charset')  
        tbl.column('published', dtype ='I', name_long ='!!Published', notnull ='y')  
        tbl.column('option', dtype ='A', notnull ='y', size ='0:64', name_long ='!!Option')  
