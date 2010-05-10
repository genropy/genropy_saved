# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('language',pkey='id',name_long='!!Language',rowcaption='$name',
                      name_plural='!!Languages')
        tbl.column('id',size='22',group='_',name_long='!!Id')
        tbl.column('name',name_long='!!Name')
        tbl.column('url',name_long='!!Url')