# encoding: utf-8
from gnr.core.gnrbag import Bag, BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('movie_companies', pkey='id', name_long='!!Movie Companies')
        tbl.column('id',dtype ='I', notnull ='y', name_long ='!!Id',group='_')  
        tbl.column('movie_id', dtype ='I', name_long ='!!Movie_Id', notnull ='y',group='_').relation('imdb.title.id',relation_name='actor',
                                                                                              one_name='Movie',many_name='Companies') 
        tbl.column('company_id', dtype ='I', name_long ='!!Company_Id', notnull ='y',group='_').relation('imdb.company_name.id',relation_name='actor',
                                                                                              one_name='Company',many_name='Movies')
        tbl.column('company_type_id', dtype ='I', name_long ='!!Company_Type_Id', notnull ='y',group='_').relation('imdb.company_type.id',relation_name='actor',
                                                                                              one_name='Type',many_name='Movies')
        tbl.column('note', dtype ='T', name_long ='!!Note')  
