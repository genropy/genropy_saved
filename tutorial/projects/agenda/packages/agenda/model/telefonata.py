# encoding: utf-8

# import datetime

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('telefonata', pkey='id', rowcaption='$cognome',
                          name_long='!!Call', name_plural='!!Calls')
        self.sysFields(tbl)
        tbl.column('giorno',dtype='D',name_long='!!Day')
        tbl.column('ora',dtype='H',name_long='!!Hour')
        tbl.column('destinatario_id',size=':22',name_long='!!Receiver').relation('agenda.staff.id',mode='foreignkey')
        tbl.aliasColumn('destinatario',relation_path='@destinatario_id.@anagrafica_id.cognome',name_long='!!Receiver')
        tbl.column('username',name_long='!!User')
        tbl.column('contatto_id',size=':22',name_long='!!Contact').relation('agenda.contatto.id',mode='foreignkey')
        tbl.column('azienda_id',size=':22',name_long='!!Company').relation('agenda.azienda.id',mode='foreignkey')
        tbl.aliasColumn('cognome',relation_path='@contatto_id.@anagrafica_id.cognome',name_long='!!Surname')
        tbl.aliasColumn('nome',relation_path='@contatto_id.@anagrafica_id.nome',name_long='!!Name')
        tbl.column('descrizione',size=':100',name_long='!!Reason of the call')
        
    #def trigger_onInserting(self, record_data):
    #    dh = datetime.datetime.now()
    #    record_data['giorno'] = dh.date()
    #    record_data['ora'] = dh.time()