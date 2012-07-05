# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('aka_title', pkey='id', name_long='aka_title')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('movie_id', _childname ='columns.movie_id', dtype ='I', name_long ='!!Movie_Id', notnull ='y')  
        tbl.column('title', _childname ='columns.title', dtype ='T', name_long ='!!Title', notnull ='y')  
        tbl.column('imdb_index', _childname ='columns.imdb_index', dtype ='A', name_long ='!!Imdb_Index', size ='0:12')  
        tbl.column('kind_id', _childname ='columns.kind_id', dtype ='I', name_long ='!!Kind_Id', notnull ='y')  
        tbl.column('production_year', _childname ='columns.production_year', dtype ='I', name_long ='!!Production_Year')  
        tbl.column('phonetic_code', _childname ='columns.phonetic_code', dtype ='A', name_long ='!!Phonetic_Code', size ='0:5')  
        tbl.column('episode_of_id', _childname ='columns.episode_of_id', dtype ='I', name_long ='!!Episode_Of_Id')  
        tbl.column('season_nr', _childname ='columns.season_nr', dtype ='I', name_long ='!!Season_Nr')  
        tbl.column('episode_nr', _childname ='columns.episode_nr', dtype ='I', name_long ='!!Episode_Nr')  
        tbl.column('note', _childname ='columns.note', dtype ='T', name_long ='!!Note')  
        tbl.column('md5sum', _childname ='columns.md5sum', dtype ='A', name_long ='!!Md5Sum', size ='0:32')  
