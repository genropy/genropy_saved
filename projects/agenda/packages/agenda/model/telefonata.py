# encoding: utf-8

# import datetime

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('telefonata', pkey='id', rowcaption='$cognome',
                          name_long='!!Telefonata', name_plural='!!Telefonate',
                          group_01='!!Principali') # group_01 è solo per prova...
        self.sysFields(tbl, group='_')
        tbl.column('giorno',dtype='D',name_long='!!Giorno',group='01')
        tbl.column('ora',dtype='H',name_long='!!Ora',group='01')
        tbl.column('destinatario_id',size=':22',name_long='!!Destinatario',
                    group='_').relation('agenda.staff.id',mode='foreignkey')
        tbl.aliasColumn('destinatario',relation_path='@destinatario_id.@anagrafica_id.cognome',
                         name_long='!!Destinatario')
        tbl.column('username',name_long='!!Utente',group='_')
        tbl.column('contatto_id',size=':22',name_long='!!Contatto',group='_').relation('agenda.contatto.id',
                    mode='foreignkey')
        tbl.column('azienda_id',size=':22',name_long='!!Azienda',
                    group='_').relation('agenda.azienda.id',mode='foreignkey')
        tbl.aliasColumn('cognome',relation_path='@contatto_id.@anagrafica_id.cognome',
                         name_long='!!Cognome',group='01')
        tbl.aliasColumn('nome',relation_path='@contatto_id.@anagrafica_id.nome',
                         name_long='!!Nome',group='01')
        tbl.column('descrizione',size=':100',name_long='!!Motivo chiamata')
        
    #def trigger_onInserting(self, record_data):
    #    dh = datetime.datetime.now()
    #    record_data['giorno'] = dh.date()
    #    record_data['ora'] = dh.time()