# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('doctemplate',pkey='name',name_long='!!Document template',
                      name_plural='!!Document templates')
        self.sysFields(tbl,id=False)
        tbl.column('name',name_long='!!Name',validate_nodup=True,unique=True,
                    validate_notnull=True,validate_notnull_error='!!Name is mandatory',
                    validate_nodup_error='!!This name is already taken')
        tbl.column('content',name_long='!!Content')
        tbl.column('metadata','X',name_long='!!Metadata')
        tbl.column('username',name_long='!!Username')
        tbl.column('version',name_long='!!Version')
        tbl.column('maintable',name_long='!!Main table')
        tbl.column('required_columns',name_long='!!Columns')