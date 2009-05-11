# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_eventlist_groupmembers',  pkey='None',name_long='jos_eventlist_groupmembers')
        tbl.column('group_id', dtype ='I', name_long ='!!Group_Id', notnull ='y')  
        tbl.column('member', dtype ='I', name_long ='!!Member', notnull ='y')  
