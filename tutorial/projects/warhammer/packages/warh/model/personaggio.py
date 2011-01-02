# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('personaggio', pkey='id', name_long='!!Personaggio', name_plural='!!Personaggi',
                        rowcaption='$nome')
        self.sysFields(tbl)
        tbl.column('sigla', name_long='!!Sigla')
        tbl.column('nome', name_long='!!Nome')
        tbl.column('razza_codice', size=':2', name_long='!!Razza').relation('warh.razza.codice', mode='foreignkey')
        tbl.column('carriera_id').relation('warh.carriera.id', mode='foreignkey', one_name='!!Carriera Attuale')
        tbl.column('ac', 'L', name_long='!!Ab.Combatt.')
        tbl.column('ab', 'L', name_long='!!Ab.Balistica')
        tbl.column('forza', 'L', name_long='!!Forza')
        tbl.column('resistenza', 'L', name_long='!!Resistenza')
        tbl.column('agilita', 'L', name_long='!!Agilità')
        tbl.column('intelligenza', 'L', name_long='!!Intelligenza')
        tbl.column('volonta', 'L', name_long='!!Volonta')
        tbl.column('simpatia', 'L', name_long='!!Simpatia')
        tbl.column('attacchi', 'L', name_long='!!Attacchi')
        tbl.column('ferite', 'L', name_long='!!Ferite')
        tbl.column('bonus_forza', 'L', name_long='!!Bonus Forza')
        tbl.column('bonus_res', 'L', name_long='!!Bonus Resistenza')
        tbl.column('mov', 'L', name_long='!!Movimento')
        tbl.column('magia', 'L', name_long='!!Magia')
        tbl.column('follia', 'L', name_long='!!Punti Follia')
        tbl.column('fato', 'L', name_long='!!Punti Fato')
        tbl.column('exp', 'L', default=0, name_long='!!Exp')

        tbl.column('ac_incr', 'L', name_long='!!Incr')
        tbl.column('ab_incr', 'L', name_long='!!Incr')
        tbl.column('forza_incr', 'L', name_long='!!Incr')
        tbl.column('resistenza_incr', 'L', name_long='!!Incr')
        tbl.column('agilita_incr', 'L', name_long='!!Incr')
        tbl.column('intelligenza_incr', 'L', name_long='!!Incr')
        tbl.column('volonta_incr', 'L', name_long='!!Incr')
        tbl.column('simpatia_incr', 'L', name_long='!!Incr')
        tbl.column('attacchi_incr', 'L', name_long='!!Incr')
        tbl.column('ferite_incr', 'L', name_long='!!Incr')
        tbl.column('bonus_forza_incr', 'L', name_long='!!Incr')
        tbl.column('bonus_res_incr', 'L', name_long='!!Incr')
        tbl.column('mov_incr', 'L', name_long='Incr')
        tbl.column('magia_incr', 'L', name_long='!!Incr')
        tbl.column('follia_incr', 'L', name_long='!!Incr')
        tbl.column('fato_incr', 'L', name_long='!!Incr')

    #       tbl.aliasColumn('razza',relation_path='@razza_codice.nome') # relation_path --> path di relazione

