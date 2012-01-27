# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable


class Table(GnrHTable):
    def config_db(self, pkg):
        tbl =  pkg.table('animal',pkey='id',name_long='!!Animal',
                      name_plural='!!Animals')
        self.sysFields(tbl)
        self.htableFields(tbl)

        tbl.column('name',name_long='!!Name')
        tbl.column('age','L',name_long='!!Age')
        tbl.column('species_id',size='22',group='_',name_long='Species id').relation('species.id', mode='foreignkey', onDelete='raise')
    
        tbl.column('abilities',
                    dtype='X',
                    name_long = '!!Abilities')