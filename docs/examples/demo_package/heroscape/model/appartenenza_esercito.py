class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('appartenenza_esercito',  pkey='id',name_long='Appartenenza Esercito')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('numero',dtype='L',name_long='Numero')
        tbl.column('unita_id',size='22',name_long='Unita', group='_').relation('heroscape.unita.id', many_group='_')
        tbl.column('esercito_id',size='22',name_long='Utente', group='_').relation('heroscape.esercito.id')
