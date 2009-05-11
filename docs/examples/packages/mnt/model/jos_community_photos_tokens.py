# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_community_photos_tokens',  pkey='None',name_long='jos_community_photos_tokens')
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('token', size ='0:200', dtype ='A', name_long ='!!Token', notnull ='y')  
        tbl.column('datetime', dtype ='DH', name_long ='!!Datetime', notnull ='y')  
