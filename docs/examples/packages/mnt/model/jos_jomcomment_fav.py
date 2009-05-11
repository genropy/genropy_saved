# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_fav',  pkey='id',name_long='jos_jomcomment_fav')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid', notnull ='y')  
        tbl.column('url', size ='0:255', dtype ='A', name_long ='!!Url', notnull ='y')  
        tbl.column('contentid', dtype ='I', name_long ='!!Contentid', notnull ='y')  
        tbl.column('option', size ='0:255', dtype ='A', name_long ='!!Option', notnull ='y')  
