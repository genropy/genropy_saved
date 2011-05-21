# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('permission',pkey='id',name_long='!!Permission',
                      name_plural='!!Permissions')
        self.sysFields(tbl)
        tbl.column('datacatalog_id',size='22',group='_',name_long='Catalog').relation('datacatalog.id', mode='foreignkey', onDelete='raise',relation_name='permissions')
        tbl.column('tag_id',name_long='!!Tag').relation('htag.id', mode='foreignkey', onDelete='raise',relation_name='permissions')
        #PERMISSIONS POSSIBILE VALUES:
        tbl.column('view_read','B',name_long='!!View Read')
        tbl.column('view_add','B',name_long='!!View Add')
        tbl.column('view_del','B',name_long='!!View Del')
        tbl.column('form_read','B',name_long='!!Form Read')
        tbl.column('form_add','B',name_long='!!Form Add')
        tbl.column('form_del','B',name_long='!!Form Del')
        tbl.column('form_upd','B',name_long='!!Form Update')
        tbl.column('column_read','B',name_long='!!Column Read')
        tbl.column('column_upd','B',name_long='!!Column Update')