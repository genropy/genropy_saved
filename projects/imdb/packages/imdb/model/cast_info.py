# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('cast_info', pkey='id', name_long='!!Cast member',rowcaption='$caption',name_plural='!!Cast members',caption_field='caption')
        tbl.column('id', _childname ='columns.id', dtype ='I', notnull ='y', name_long ='!!Id',group='_')  
        tbl.column('person_id', dtype ='I', name_long ='!!Person Id', notnull ='y',group='_').relation('imdb.name.id',
                                                                                              relation_name='movie_cast',
                                                                                              one_name='Person',many_name='Movies')
        tbl.column('movie_id', dtype ='I', name_long ='!!Movie Id', notnull ='y',group='_').relation('imdb.title.id',relation_name='cast_members',
                                                                                   one_name='Movie',many_name='Cast Members')
        tbl.column('person_role_id', dtype ='I', name_long ='!!Character Id',group='_').relation('imdb.char_name.id',relation_name='characters',
                                                                                    one_name='Character',many_name='Movies')
        tbl.column('note',dtype ='T', name_long ='!!Note')  
        tbl.column('nr_order',  dtype ='I', name_long ='!!Order')  
        tbl.column('role_id', dtype ='I', name_long ='!!Role_Id', notnull ='y',group='_').relation('imdb.role_type.id',relation_name='movies',
                                                                one_name='Role',many_name='Movies')
        tbl.aliasColumn('title',relation_path='@movie_id.title',name_long='!!Movie Title')
        tbl.aliasColumn('year',relation_path='@movie_id.production_year',name_long='!!Year',dtype='I')
        tbl.aliasColumn('person',relation_path='@person_id.name',name_long='!!Person')
        tbl.aliasColumn('role',relation_path='@role_id.role',name_long='!!Role')
        tbl.aliasColumn('character',relation_path='@person_role_id.name',name_long='!!Character')
        tbl.formulaColumn('caption',"$title || '-' || $actor || '('|| $character ||')'")
