# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_poll_date',  pkey='id',name_long='jos_poll_date')
        tbl.column('id', dtype ='L', name_long ='!!Id', notnull ='y')  
        tbl.column('date', dtype ='DH', name_long ='!!Date', notnull ='y')  
        tbl.column('vote_id', dtype ='I', name_long ='!!Vote_Id', notnull ='y')  
        tbl.column('poll_id', dtype ='I', name_long ='!!Poll_Id', notnull ='y')  
