class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('combo_unita',  pkey='id',name_long=u'!!Combo unita', rowcaption='nome')
        tbl.column('combo_id',size='22',group='_',readOnly='y',name_long='Combo Id').relation('heroscape.combo.id')
        tbl.column('unita_id',size='22',group='_',readOnly='y',name_long=u'Unita Id').relation('heroscape.unita.id', many_group='_')
