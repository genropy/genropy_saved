# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('movie_link', pkey='id', name_long='movie_link')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('movie_id', _childname ='columns.movie_id', dtype ='I', name_long ='!!Movie_Id', notnull ='y').relation('imdb.title.id')
        tbl.column('linked_movie_id', _childname ='columns.linked_movie_id', dtype ='I', name_long ='!!Linked_Movie_Id', notnull ='y').relation('imdb.title.id')
        tbl.column('link_type_id', _childname ='columns.link_type_id', dtype ='I', name_long ='!!Link_Type_Id', notnull ='y').relation('imdb.link_type.id')
