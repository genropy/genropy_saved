# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_messages',  pkey='id',name_long='jos_fc_messages')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('toconnid', dtype ='A', name_long ='!!Toconnid', size ='0:32')  
        tbl.column('touserid', dtype ='I', name_long ='!!Touserid')  
        tbl.column('toroomid', dtype ='I', name_long ='!!Toroomid')  
        tbl.column('command', dtype ='A', notnull ='y', size ='0:255', name_long ='!!Command')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('roomid', dtype ='I', name_long ='!!Roomid')  
        tbl.column('txt', dtype ='T', name_long ='!!Txt')  
        tbl.column('chatid', dtype ='I', name_long ='!!Chatid', notnull ='y')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
