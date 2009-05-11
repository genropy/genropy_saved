class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('voto_mappa',  pkey='id',name_long='Voto mappa')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('voto', dtype='L',name_long='Voto')
        tbl.column('motivazione',name_long='Motivazione')
        tbl.column('mappa_id',size='22',name_long='Unita').relation('heroscape.mappa.id')
        tbl.column('user_id',size='22',name_long='Utente').relation('adm.user.id')
