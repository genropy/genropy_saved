# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_status',  pkey='None',name_long='jos_community_status')
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('status', dtype ='T', name_long ='!!Status', notnull ='y')  
        tbl.column('posted_on', dtype ='DH', name_long ='!!Posted_On', notnull ='y')  
