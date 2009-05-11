# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_eventlist_register',  pkey='id',name_long='jos_eventlist_register')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('event', dtype ='I', name_long ='!!Event', notnull ='y')  
        tbl.column('uid', dtype ='I', name_long ='!!Uid', notnull ='y')  
        tbl.column('uregdate', dtype ='A', notnull ='y', size ='0:50', name_long ='!!Uregdate')  
        tbl.column('uip', dtype ='A', notnull ='y', size ='0:15', name_long ='!!Uip')  
