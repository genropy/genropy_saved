# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('dev_lang',pkey='id',name_long='!!Developer languages',
                      name_plural='!!Developer languages',broadcast=True)
        tbl.column('id',size='22',group='_',name_long='Id')
        tbl.column('developer_id',size='22',group='_',name_long='!!Developer').relation('developer.id',mode='foreignkey',onDelete='cascade')
        tbl.column('language_id',size='22',group='_',name_long='!!Language').relation('language.id',mode='foreignkey',onDelete='cascade')
        tbl.column('level',dtype='L',name_long='!!Level')