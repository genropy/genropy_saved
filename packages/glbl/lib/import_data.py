#!/usr/bin/env python
# encoding: utf-8
"""
import_data.py

Created by Saverio Porcari on 2007-08-27.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import random,datetime
from gnr.app.gnrapp import GnrApp

import md5

def importRegione(db, filepath):
    tbl=db.table('glbl.regione')
    f=file(filepath)
    t=f.read()
    lines=t.split('\n')
    d={}
    for l in lines:
        if l:
            r=l.split(';')
            record={}
            d[r[4]]=r[0]
            record['sigla']=r[0].strip()
            record['nome']=r[1].strip()
            record['zona']=r[2].strip()
            record['ordine']=r[3].strip()
            record['codice_istat']=r[4].strip()
            tbl.insert(record)
    return d


def importLocalita(db, filepath):
    tbl=db.table('glbl.localita')
    f=file(filepath)
    t=f.read()
    lines=t.split('\n')
    for l in lines:
        record={}
        if l:
            record['nome']=l[:35].strip()
            record['provincia']=l[35:37].strip()
            record['CAP']=l[50:55]
            record['prefisso_tel']=l[60:66].strip()
            record['codice_comune']=l[68:75].strip()
            record['codice_istat']=l[78:86].strip()
            tbl.insert(record)
            
def importProvincia(db, filepath, regdict):
    tbl=db.table('glbl.provincia')
    f=file(filepath)
    t=f.read()
    lines=t.split('\n')
    for l in lines:
        if l:
            r=l.split(',')
            record={}
            record['sigla']=r[5].strip()
            record['nome']=r[4]
            record['regione']=regdict[r[1]]
            record['codice_istat']=r[3].strip()
            tbl.insert(record)
    
def importStradario(db, filepath):
    tbl=db.table('glbl.stradario_cap')
    f=file(filepath)
    t=f.read()
    lines=t.split('>\r\n<')
    lines[0]=lines[0][1:]
    for l in lines:
        r=l.split(',')
        record={}
        record['id']=tbl.newPkeyValue()
        record['cap']=r[9].strip()[:8]
        record['provincia']=r[0].strip()
        record['comune']=r[1].strip()
        record['comune2']=r[2].strip()
        record['frazione']=r[3].strip()
        record['frazione2']=r[4].strip()
        record['topo']=r[5].strip()
        record['topo2']=r[6].strip()
        record['pref']=r[7].strip()
        record['n_civico']=r[8].strip()
        tbl.insert(record)
        print record['topo']
    print 'fine righe'




if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/condox').db
    regdict=importRegione(db, '/Users/saverioporcari/Desktop/regioni.txt')
    importProvincia(db, '/Users/saverioporcari/Desktop/regioni_province.txt', regdict)
    importLocalita(db, '/Users/saverioporcari/Desktop/comuni.txt')
    db.commit()
    importStradario(db, '/Users/saverioporcari/Desktop/filecap')
    db.commit()
        
    
    print 'update done'
