# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('contatto', pkey='id', rowcaption='@anagrafica_id.nome, @anagrafica_id.cognome: %s %s',
                          name_long='!!Contatto', name_plural='!!Contatti')
        self.sysFields(tbl, group='_')
        tbl.column('anagrafica_id',size=':22',name_long='!!Anagrafica id').relation('sw_base.anagrafica.id', mode='foreignkey')
        tbl.column('azienda_id',size=':22',name_long='!!Azienda').relation('agenda.azienda.id', relation_name='contatti',mode='foreignkey')
        tbl.column('interno',size=':15',name_long ='!!Interno')
        tbl.column('ruolo',size=':30',name_long ='!!Ruolo')