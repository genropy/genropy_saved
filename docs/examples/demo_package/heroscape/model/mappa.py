class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('mappa',  pkey='id',name_long='Mappa', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':20',name_long='Nome')
        tbl.column('num_giocatori', size=':20', name_long='Num giocatori')
        tbl.column('regole_speciali',name_long='Regole speciali')
        tbl.column('obiettivi',name_long='Obiettivi')
        tbl.column('data_inserimento', dtype='D',name_long='Data')
        tbl.column('url',name_long='Url')
        tbl.column('user_id',size='22',name_long='Utente').relation('adm.user.id')
