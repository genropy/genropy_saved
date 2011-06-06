# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('media',  pkey='id',name_long='!!Media',
                      name_plural='!!Media')
        self.sysFields(tbl)
        tbl.column('page_id', name_long='!!Page').relation('website.page.id')
        tbl.column('title',name_long='!!Title')
        tbl.column('info_text',name_long='!!Info text')
        tbl.column('flib_id',size='22',name_long='!!File').relation('flib.item.id', 
                                                            mode='foreignkey',onDelete='cascade')