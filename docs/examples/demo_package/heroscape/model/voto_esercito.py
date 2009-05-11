class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('voto_esercito',  pkey='id',name_long='Voto esercito')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('voto', dtype='L',name_long='Voto')
        tbl.column('motivazione',name_long='Motivazione')
        tbl.column('esercito_id',size='22',name_long='Unita', group='_').relation('heroscape.esercito.id')
        tbl.column('user_id',size='22',name_long='Utente', group='_').relation('adm.user.id')
