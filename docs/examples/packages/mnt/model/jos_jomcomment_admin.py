# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_admin',  pkey='sid',name_long='jos_jomcomment_admin')
        tbl.column('sid', dtype ='A', notnull ='y', size ='0:128', name_long ='!!Sid')  
        tbl.column('commentid', dtype ='I', name_long ='!!Commentid', notnull ='y')  
        tbl.column('action', dtype ='A', notnull ='y', size ='0:128', name_long ='!!Action')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
