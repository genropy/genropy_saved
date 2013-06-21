# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('role_type', pkey='id', name_long='!!Role',name_plural='!!Roles',caption_filed='role',rowcaption='$role',lookup=True)
        tbl.column('id', dtype ='I', notnull ='y', name_long ='!!Id')  
        tbl.column('role',  dtype ='A', notnull ='y', size ='0:32', name_long ='!!Role')  
