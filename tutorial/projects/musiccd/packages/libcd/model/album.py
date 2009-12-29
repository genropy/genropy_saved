# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('album',  pkey='id',name_long='!!Album',
                      name_plural='!!Albums',rowcaption='$title')
        self.sysFields(tbl)
        tbl.column('title',size=':40',name_long='!!Title')
        tbl.column('year','L',name_long='!!Year')
        tbl.column('rating','L',name_long='!!Rating')
        tbl.column('artist_id',size='22',group='_').relation('artist.id',mode='foreignkey',onDelete='cascade')
        