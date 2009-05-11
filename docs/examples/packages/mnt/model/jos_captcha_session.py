# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_captcha_session',  pkey='id',name_long='jos_captcha_session')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('sessionid', dtype ='A', notnull ='y', size ='0:64', name_long ='!!Sessionid')  
        tbl.column('password', dtype ='A', notnull ='y', size ='0:8', name_long ='!!Password')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
