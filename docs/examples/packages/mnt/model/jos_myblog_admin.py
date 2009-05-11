# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_admin',  pkey='sid',name_long='jos_myblog_admin')
        tbl.column('sid', size ='0:128', dtype ='A', name_long ='!!Sid', notnull ='y')  
        tbl.column('cid', dtype ='I', name_long ='!!Cid', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
