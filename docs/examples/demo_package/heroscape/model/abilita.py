class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('abilita',  pkey='id',name_long=u'Abilita', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('unita_id',size='22',name_long='Unita ID').relation('heroscape.unita.id', many_group='_')
        tbl.column('nome', size=':42',name_long='Nome', indexed='y')
        tbl.column('descrizione',name_long='Descrizione')