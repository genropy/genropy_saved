# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('complete_cast', pkey='id', name_long='complete_cast')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('movie_id', _childname ='columns.movie_id', dtype ='I', name_long ='!!Movie_Id')  
        tbl.column('subject_id', _childname ='columns.subject_id', dtype ='I', name_long ='!!Subject_Id', notnull ='y')  
        tbl.column('status_id', _childname ='columns.status_id', dtype ='I', name_long ='!!Status_Id', notnull ='y')  
