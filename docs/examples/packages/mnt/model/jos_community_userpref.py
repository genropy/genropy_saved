# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_userpref',  pkey='None',name_long='jos_community_userpref')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('params', dtype ='T', name_long ='!!Params', notnull ='y')  
