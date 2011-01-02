# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('razza', pkey='codice', name_long='!!Razza', name_plural='!!Razze', rowcaption='$codice,$nome')
        self.sysFields(tbl, id=False)
        tbl.column('codice', size=':2', name_long='!!Codice')
        tbl.column('nome', name_long='!!Nome')
        tbl.column('descrizione', name_long='!!Descrizione')
        tbl.column('colore', name_long='!!Colore')
        tbl.column('ac_base', 'L', default=0, name_long='!!Ab. Combattimento')
        tbl.column('ab_base', 'L', default=0, name_long='!!Ab. Balistica')
        tbl.column('f_base', 'L', default=0, name_long='!!Forza')
        tbl.column('r_base', 'L', default=0, name_long='!!Resistenza')
        tbl.column('ag_base', 'L', default=0, name_long='!!Agilità')
        tbl.column('int_base', 'L', default=0, name_long='!!Intelligenza')
        tbl.column('vol_base', 'L', default=0, name_long='!!Volontà')
        tbl.column('simp_base', 'L', default=0, name_long='!!Simpatia')
        tbl.column('att_base', 'L', default=0, name_long='!!Attacchi')
        tbl.column('fer_base', 'X', name_long='!!Ferite')
        tbl.column('b_forza_base', 'L', default=0, name_long='!!Bonus Forza')
        tbl.column('b_res_base', 'L', default=0, name_long='!!Bonus Resistenza')
        tbl.column('mov_base', 'L', default=0, name_long='!!Movimento')
        tbl.column('magia_base', 'L', default=0, name_long='!!Magia')
        tbl.column('fol_base', 'L', default=0, name_long='!!Punti Follia')
        tbl.column('pf_base', 'X', default=0, name_long='!!Punti Fato')
        
