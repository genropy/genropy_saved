# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('char_name', pkey='id', name_long='!!Character',name_plural='!!Characters',caption_field='name',rowcaption='$name')
        tbl.column('id',dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('name',  dtype ='T', name_long ='!!Character', notnull ='y',indexed='True')  
        tbl.column('imdb_index',  dtype ='A', name_long ='!!Imdb_Index', size ='0:12')  
        tbl.column('imdb_id', dtype ='I', name_long ='!!Imdb_Id')  
        tbl.column('name_pcode_nf',  dtype ='A', name_long ='!!Name_Pcode_Nf', size ='0:5')  
        tbl.column('surname_pcode', dtype ='A', name_long ='!!Surname_Pcode', size ='0:5')  
        tbl.column('md5sum', _childname ='columns.md5sum', dtype ='A', name_long ='!!Md5Sum', size ='0:32')  
