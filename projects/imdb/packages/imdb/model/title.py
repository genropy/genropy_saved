# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('title', pkey='id', name_long='!!Title',name_plural='!!Titles',caption_field='caption',rowcaption='$caption')
        tbl.column('id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('title',dtype ='T', name_long ='!!Title', notnull ='y',indexed=True)  
        tbl.column('imdb_index',  dtype ='A', name_long ='!!Imdb_Index', size ='0:12',group='_')  
        tbl.column('kind_id',  dtype ='I', name_long ='!!Kind', notnull ='y',group='_').relation('imdb.kind_type.id',
                                                                                              relation_name='kind_type',
                                                                                              one_name='!!Kind',many_name='!!Movies')
        tbl.column('production_year', dtype ='I', name_long ='!!Year',indexed=True)  
        tbl.column('imdb_id',  dtype ='I', name_long ='!!Imdb_Id',group='_')  
        tbl.column('phonetic_code',dtype ='A', name_long ='!!Phonetic_Code', size ='0:5',group='_')  
        tbl.column('episode_of_id',  dtype ='I', name_long ='!!Episode_Of_Id',group='_')  
        tbl.column('season_nr',  dtype ='I', name_long ='!!Season_Nr')  
        tbl.column('episode_nr',dtype ='I', name_long ='!!Episode_Nr')  
        tbl.column('series_years',  dtype ='A', name_long ='!!Series_Years', size ='0:49')  
        tbl.column('md5sum',  dtype ='A', name_long ='!!Md5Sum', size ='0:32',group='_')  
        tbl.formulaColumn('caption',"$title || '(' || $production_year || ')'")
        tbl.aliasColumn('kind',relation_path='@kind_id.kind')
