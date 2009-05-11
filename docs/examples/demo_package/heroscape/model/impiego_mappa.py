class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('impiego_mappa',  pkey='id',name_long='Impiego Mappa')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('numero',dtype='L',name_long='Numero')
        tbl.column('prodotto_id',size='22',name_long='Prodotto').relation('heroscape.prodotto.id')
        tbl.column('mappa_id',size='22',name_long='Mappa').relation('heroscape.mappa.id')
