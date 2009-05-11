# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_bans',  pkey='None',name_long='jos_fc_bans')
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('banneduserid', dtype ='I', name_long ='!!Banneduserid')  
        tbl.column('roomid', dtype ='I', name_long ='!!Roomid')  
        tbl.column('ip', dtype ='A', name_long ='!!Ip', size ='0:16')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
