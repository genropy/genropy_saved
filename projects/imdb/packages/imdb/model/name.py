# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('name', pkey='id', name_long='Person',rowcaption='$name',caption_field='name',name_plural='People')
        tbl.column('id',  dtype ='I', notnull ='y', name_long ='!!Id',group='_')  
        tbl.column('name', dtype ='T', name_long ='!!Name', notnull ='y',indexed=True)  
        tbl.column('imdb_index', dtype ='A', name_long ='!!Imdb_Index', size ='0:12',group='_')  
        tbl.column('imdb_id', dtype ='I', name_long ='!!Imdb_Id',group='_')  
        tbl.column('gender', dtype ='A', name_long ='!!Gender', size ='0:1')  
        tbl.column('name_pcode_cf',  dtype ='A', name_long ='!!Name_Pcode_Cf', size ='0:5',group='_')  
        tbl.column('name_pcode_nf',  dtype ='A', name_long ='!!Name_Pcode_Nf', size ='0:5',group='_')  
        tbl.column('surname_pcode', dtype ='A', name_long ='!!Surname_Pcode', size ='0:5',group='_')  
        tbl.column('md5sum', _childname ='columns.md5sum', dtype ='A', name_long ='!!Md5Sum', size ='0:32',group='_')  
