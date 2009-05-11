#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag


class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('tariffa',  pkey='id',name_long='!!Tariffa', name_plural='!!Tariffe',
        rowcaption='codice,nome,@evento_id.codice: %s-%s-%s')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('codice', size=':12',name_long='!!Codice')
        tbl.column('descrizione', size=':40', name_long='!!Descrizione')
        tbl.column('importo','R', name_long='!!Importo')
        tbl.column('tipo',size=':12', name_long='!!Tipo')
        tbl.column('decorrenza','D', name_long='!!Decorrenza')
        tbl.column('scadenza','D', name_long='!!Scadenza')
        tbl.column('evento_id', size='22',name_long='!!Evento').relation('assopy.evento.id', mode='foreignkey')
        tbl.column('aliquota_iva', size='2', name_long='!!Aliquota IVA')
        tbl.column('ingressi_omaggio', 'L', name_long='!!Ingressi Omaggio')
        tbl.column('prezzo_ivato', 'B', name_long='!!Prezzo Ivato')
        tbl.column('dicitura_it', name_long='!!Dicitura Italiana')
        tbl.column('dicitura_en', name_long='!!Dicitura Inglese')

    def tariffeCorrenti(self,evento,workdate, tp):
        tariffe = self.query('*',
                              where="""$evento_id   = :currevt AND
                                       $tipo   ILIKE :tp AND
                                       $decorrenza <=:workdate AND
                                       $scadenza   >=:workdate """, 
                             currevt=evento,
                             workdate=workdate,
                             tp=tp
                             ).fetch()
        result=Bag()
        for t in tariffe:
            result[t['tipo']]=Bag(t.items())
        return result
        
    
    def populate(self):
        import datetime
        
        evento = self.pkg.attributes['evento_corrente']
        eventoRecord= self.db.table('assopy.evento').record(codice=evento).output('bag')
        idevento = eventoRecord['id']

        tariffe = (
            ('TESTSTU08','TEST Studenti'       ,'TK_STU',  1.0, '2008-01-01',  '2008-03-22', '20', 0, True),
            ('TESTPRO08','TEST Professionisti' ,'TK_PRO',  2.0, '2008-01-01',  '2008-03-22','20', 0, True),
            ('EARLSTU08','Early Bird Studenti'       ,'TK_STU',  50.0, '2008-03-23', '2008-04-10','20', 0, True),
            ('EARLPRO08','Early Bird Professionisti' ,'TK_PRO',  70.0, '2008-03-23', '2008-04-10','20', 0, True),
            ('LATESTU08','Late Bird Studenti'        ,'TK_STU',  70.0, '2008-04-11', '2008-05-9', '20', 0, True),
            ('LATEPRO08','Late Bird Professionisti'  ,'TK_PRO',  90.0, '2008-04-11', '2008-05-9', '20', 0, True),
            ('DESKSTU08','On Desk Studenti'          ,'TK_STU', 120.0, '2008-05-10', '2008-05-14','20', 0, True),
            ('DESKPRO08','On Desk Professionisti'    ,'TK_PRO', 120.0, '2008-05-10', '2008-05-14','20', 0, True),
            ('_DONAZ'   ,'Donazione'                 ,'DON'   ,   0.0, None, None,'00', 0, True),
            ('SPBRONZE'   ,'Sponsorizzazione Bronze'     ,'SPO'   ,    500.0, None, None,'20', 1, False),
            ('SPSILVER'   ,'Sponsorizzazione Silver'     ,'SPO'   ,   1000.0, None, None,'20', 2, False),
            ('SPGOLD'   ,'Sponsorizzazione Gold'         ,'SPO'   ,   1500.0, None, None,'20', 3, False),
            ('SPPLATINUM'   ,'Sponsorizzazione Platinum' ,'SPO'   ,   3000.0, None, None,'20', 6, False),
            ('SPDIAMOND'   ,'Sponsorizzazione Diamond'   ,'SPO'   ,   5000.0, None, None,'20',10, False),
            ('_OMG'   ,'Omaggio'   ,'OMG'   ,   0.0, None, None,'00', 0, True)
        )
        for t in tariffe:
            tariffa = dict(
                codice = t[0],
                descrizione = t[1],
                tipo = t[2],
                importo = t[3],
                decorrenza = t[4],
                scadenza = t[5],
                evento_id = idevento,
                aliquota_iva = t[6],
                ingressi_omaggio = t[7],
                prezzo_ivato = t[8]
                
            )
            self.recordCoerceTypes(tariffa,'NULL')
            self.insert(tariffa)
            