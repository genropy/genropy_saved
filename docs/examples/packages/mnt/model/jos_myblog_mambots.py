# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_myblog_mambots',  pkey='mambot_id',name_long='jos_myblog_mambots')
        tbl.column('mambot_id', dtype ='I', name_long ='!!Mambot_Id', notnull ='y')  
        tbl.column('my_published', dtype ='I', name_long ='!!My_Published', notnull ='y')  
