# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_reported',  pkey='commentid',name_long='jos_jomcomment_reported')
        tbl.column('commentid', dtype ='I', name_long ='!!Commentid', notnull ='y')  
