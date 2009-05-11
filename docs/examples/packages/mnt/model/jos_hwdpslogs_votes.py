# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_hwdpslogs_votes',  pkey='id',name_long='jos_hwdpslogs_votes')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('videoid', dtype ='I', name_long ='!!Videoid', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('vote', dtype ='I', name_long ='!!Vote', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
