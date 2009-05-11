class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('generale',  pkey='id',name_long='Generale', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':42',name_long='Nome', indexed='y')
        tbl.column('colore', size=':10',name_long='Colore', indexed='y')
        tbl.column('descrizione',name_long='Descrizione')