class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('possesso_prodotto',  pkey='id',name_long='Possesso prodotto')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('numero', dtype='L',name_long='Numero')
        tbl.column('prodotto_id',size='22',name_long='Prodotto Id',group='_').relation('heroscape.prodotto.id')
        tbl.column('user_id',size='22',name_long='Proprietario Id',group='_').relation('adm.user.id')
