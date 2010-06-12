# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('personaggio',pkey='id',name_long='!!Personaggio',name_plural='!!Personaggi')
        self.sysFields(tbl) # aggiunge i campi ID, data inserimento, INS, MOD, DEL
        tbl.column('sigla',name_long='!!Sigla') # creo una casella; sintassi: tbl.column('nome_casella',name_long='nome visualizzato')
        tbl.column('nome',name_long='!!Nome')
        tbl.column('razza_codice',size=':2',name_long='!!Razza').relation('warh.razza.codice',mode='foreignkey')
                                                            #.relation('nome_del_packages.nome_della_table.nome_di_una_tblColumn)
        tbl.column('ac','L',name_long='!!AC')
        tbl.column('ab','L',name_long='!!AB')
        tbl.column('forza','L',name_long='!!Forza')
        tbl.column('resistenza','L',name_long='!!Resistenza')
        tbl.column('agilita','L',name_long='!!Agilita')
        tbl.column('intelligenza','L',name_long='!!Intelligenza')
        tbl.column('volonta','L',name_long='!!Volonta')
        tbl.column('simpatia','L',name_long='!!Simpatia')
        tbl.column('attacchi','L',name_long='!!Attacchi')
        tbl.column('ferite','L',name_long='!!Ferite')
        tbl.column('bonus_forza','L',name_long='!!Bonus Forza')
        tbl.column('bonus_res','L',name_long='!!Bonus Resistenza')
        tbl.column('mov','L',name_long='!!Movimento')
        tbl.column('magia','L',name_long='!!Magia')
        tbl.column('follia','L',name_long='!!Punti Follia')
        tbl.column('fato','L',name_long='!!Punti Fato')