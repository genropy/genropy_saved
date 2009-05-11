class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('possesso_unita',  pkey='id',name_long='Possesso Unita', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('numero', dtype='L',name_long='Numero')
        tbl.column('unita_id',size='22',name_long='Unita',group='_').relation('heroscape.unita.id', many_group='_')
        tbl.column('user_id',size='22',name_long='Utente',group='_').relation('adm.user.id')
