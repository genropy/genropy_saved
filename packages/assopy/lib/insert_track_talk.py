#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import random,datetime
from gnr.app.gnrapp import GnrApp

def insertAttivitaSettore(db ):
    insertMany(db,'Insegnante,Imprenditore,Sviluppatore,Studente,Web Designer', 'assopy.attivita')
    insertMany(db,'Istruzione,Ricerca,Gestionale,Aziendale,Web Technology', 'assopy.settore')

    
def insertMany(db, lines, tblname):
    tbl=db.table(tblname)
    for a in lines.split(','):
        record = dict(id = tbl.newPkeyValue(), descrizione = a)
        tbl.insert(record)
        

def insertTrack(db):
    tbl=db.table('assopy.track')
    tbl.insert(dict(id = tbl.newPkeyValue(), titolo = 'Scoprire Python', codice='SP'))
    tbl.insert(dict(id = tbl.newPkeyValue(), titolo = 'Diffondere Python', codice='DP'))
    tbl.insert(dict(id = tbl.newPkeyValue(), titolo = 'Imparare Python', codice='IP'))



if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/assopy').db
    insertAttivitaSettore(db)
    insertTrack(db)
    db.commit()
    print "Done"
    
