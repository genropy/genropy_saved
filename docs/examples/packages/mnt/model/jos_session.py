# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_session',  pkey='session_id',name_long='jos_session')
        tbl.column('username', dtype ='A', name_long ='!!Username', size ='0:150')  
        tbl.column('time', dtype ='A', name_long ='!!Time', size ='0:14')  
        tbl.column('session_id', dtype ='A', notnull ='y', size ='0:200', name_long ='!!Session_Id')  
        tbl.column('guest', dtype ='I', name_long ='!!Guest')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('usertype', dtype ='A', name_long ='!!Usertype', size ='0:50')  
        tbl.column('gid', dtype ='I', name_long ='!!Gid', notnull ='y')  
        tbl.column('client_id', dtype ='I', name_long ='!!Client_Id', notnull ='y')  
        tbl.column('data', dtype ='T', name_long ='!!Data')  
