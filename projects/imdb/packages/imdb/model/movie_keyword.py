# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('movie_keyword', pkey='id', name_long='movie_keyword')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('movie_id', _childname ='columns.movie_id', dtype ='I', name_long ='!!Movie_Id', notnull ='y')  
        tbl.column('keyword_id', _childname ='columns.keyword_id', dtype ='I', name_long ='!!Keyword_Id', notnull ='y')  
