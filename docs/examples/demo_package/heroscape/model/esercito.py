class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('esercito',  pkey='id',name_long='Esercito', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':20',name_long='Nome')
        tbl.column('data_inserimento', dtype='D',name_long='Data')
        tbl.column('punteggio', size=':20',name_long='Nome')
        tbl.column('user_id',size='22',name_long='Utente').relation('adm.user.id')
