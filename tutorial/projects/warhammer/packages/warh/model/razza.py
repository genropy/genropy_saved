# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('razza',pkey='codice',name_long='!!Razza',
                      name_plural='!!Razze',rowcaption='$codice,$nome')
        self.sysFields(tbl,id=False)
        tbl.column('codice',size=':2',name_long='!!Codice')
        tbl.column('nome',name_long='!!Nome')
        tbl.column('descrizione',name_long='!!Descrizione')
        tbl.column('colore',name_long='!!Colore')
        tbl.column('ac_base','L',name_long='!!AC base')
        tbl.column('ab_base','L',name_long='!!AB base')
        tbl.column('f_base','L',name_long='!!Forza base')
        tbl.column('r_base','L',name_long='!!Resistenza base')
        tbl.column('pf_base','L',name_long='!!Punti Fato base')
        