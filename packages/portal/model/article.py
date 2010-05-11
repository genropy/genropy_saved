# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('article',pkey='id',name_long='!!Article',
                      name_plural='!!Article')
        self.sysFields(tbl)
        tbl.column('subject',name_long='!!Subject')
        tbl.column('summary',name_long='!!Summary')
        tbl.column('article',name_long='!!Article')
        tbl.column('tags',name_long='!!Tags')
        tbl.column('author',size='22',group='_').relation('staff.id',mode='foreignkey')
