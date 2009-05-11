# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_connections',  pkey='id',name_long='jos_fc_connections')
        tbl.column('id', dtype ='A', notnull ='y', size ='0:32', name_long ='!!Id')  
        tbl.column('updated', dtype ='DH', name_long ='!!Updated', notnull ='y')  
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('roomid', dtype ='I', name_long ='!!Roomid')  
        tbl.column('state', dtype ='I', name_long ='!!State', notnull ='y')  
        tbl.column('color', dtype ='I', name_long ='!!Color')  
        tbl.column('start', dtype ='I', name_long ='!!Start')  
        tbl.column('lang', dtype ='A', name_long ='!!Lang', size ='2')  
        tbl.column('ip', dtype ='A', name_long ='!!Ip', size ='0:16')  
        tbl.column('tzoffset', dtype ='I', name_long ='!!Tzoffset')  
        tbl.column('chatid', dtype ='I', name_long ='!!Chatid', notnull ='y')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
