# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('person_music', pkey='id', rowcaption='@music_id.title',
                        name_long='!!Cast', name_plural='!!Casts')
        tbl.column('id', size='22', group='_', readOnly=True, name_long='Id')
        tbl.column('music_id', size='22', name_long='!!Music id').relation('music.id', mode='foreignkey')
        tbl.column('person_id', size='22', name_long='!!Person id').relation('person.id', mode='foreignkey')