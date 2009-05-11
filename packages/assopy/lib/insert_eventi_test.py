#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import random,datetime
from gnr.app.gnrapp import GnrApp

def insertEventi(db):
    id = db.table('assopy.evento').newPkeyValue()
    evento = dict(
        id = id,
        codice='pycon2',
        data_inizio = datetime.date(2008,6,1),
        data_fine = datetime.date(2008,6,4),
        titolo = 'PyConDue',
        descrizione = 'Seconda conferenza italiana dedicata al linguaggio Python.',
        edizione = 2,
        homepage = 'http://www.pycon.it',
        scadenza_importo_1 = datetime.date(2008,4,1),
        scadenza_importo_2 = datetime.date(2008,5,1)
    )
    db.table('assopy.evento').insert(evento)
    return id

def insertTariffe(db, idevento):
    tariffe = (
        ('TESTSTU08','TEST Studenti'       ,'TK_STU',  1.0, datetime.date(2008,1,1),  datetime.date(2008,3,22),'20'),
        ('TESTPRO08','TEST Professionisti' ,'TK_PRO',  2.0, datetime.date(2008,1,1),  datetime.date(2008,3,22),'20'),
        ('EARLSTU08','Early Bird Studenti'       ,'TK_STU',  50.0, datetime.date(2008,3,23),  datetime.date(2008,4,10),'20'),
        ('EARLPRO08','Early Bird Professionisti' ,'TK_PRO',  70.0, datetime.date(2008,3,23),  datetime.date(2008,4,10),'20'),
        ('LATESTU08','Late Bird Studenti'        ,'TK_STU',  70.0, datetime.date(2008,4,11), datetime.date(2008,5,9), '20'),
        ('LATEPRO08','Late Bird Professionisti'  ,'TK_PRO',  90.0, datetime.date(2008,4,11), datetime.date(2008,5,9), '20'),
        ('DESKSTU08','On Desk Studenti'          ,'TK_STU', 120.0, datetime.date(2008,5,10), datetime.date(2008,5,14),'20'),
        ('DESKPRO08','On Desk Professionisti'    ,'TK_PRO', 120.0, datetime.date(2008,5,10), datetime.date(2008,5,14),'20'),
        ('_DONAZ'   ,'Donazione'                 ,'DON'   ,   0.0, None, None,'00')
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
            aliquota_iva = t[6]
        )
        db.table('assopy.tariffa').insert(tariffa)
    


if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/assopy').db
    idevento = insertEventi(db)
    insertTariffe(db, idevento)
    db.commit()
    print "Done"
    
    