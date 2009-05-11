# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_msg_recepient',  pkey='None',name_long='jos_community_msg_recepient')
        tbl.column('msg_id', dtype ='I', name_long ='!!Msg_Id', notnull ='y')  
        tbl.column('msg_parent', dtype ='I', name_long ='!!Msg_Parent', notnull ='y')  
        tbl.column('msg_from', dtype ='I', name_long ='!!Msg_From', notnull ='y')  
        tbl.column('to', dtype ='I', name_long ='!!To', notnull ='y')  
        tbl.column('bcc', dtype ='I', name_long ='!!Bcc')  
        tbl.column('is_read', dtype ='I', name_long ='!!Is_Read')  
        tbl.column('deleted', dtype ='I', name_long ='!!Deleted')  
