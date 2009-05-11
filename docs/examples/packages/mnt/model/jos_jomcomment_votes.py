# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_jomcomment_votes',  pkey='id',name_long='jos_jomcomment_votes')
        tbl.column('id', dtype ='I', name_long ='!!Id', notnull ='y')  
        tbl.column('ip', size ='0:32', dtype ='A', name_long ='!!Ip', notnull ='y')  
        tbl.column('voted_on', dtype ='DH', name_long ='!!Voted_On', notnull ='y')  
        tbl.column('commentid', dtype ='I', name_long ='!!Commentid', notnull ='y')  
        tbl.column('option', size ='0:128', dtype ='A', name_long ='!!Option', notnull ='y')  
        tbl.column('value', dtype ='I', name_long ='!!Value', notnull ='y')  
