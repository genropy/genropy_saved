class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('prodotto',  pkey='id',name_long='Prodotto', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':42',name_long='Nome', indexed='y')
        tbl.column('anno', dtype='L',name_long='Anno uscita', indexed='y')
        tbl.column('sigla', size=':10',name_long='Sigla', indexed='y')
        tbl.column('descrizione',name_long='Descrizione')
        tbl.column('scenario',dtype='B', name_long='Scenario')