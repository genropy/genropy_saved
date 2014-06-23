#!/usr/bin/env python
# encoding: utf-8
"""
import_data.py

Created by Saverio Porcari on 2007-08-27.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import random, datetime
from gnr.app.gnrapp import GnrApp

import md5

def importSigleNaz(db, filepath):
    tbl = db.table('glbl.nazione')
    f = file(filepath)
    t = f.read()
    lines = t.split('\n')
    d = {}
    for l in lines:
        if l:
            r = l.split(';')
            record = {}
            record['sigla'] = r[1].strip()
            record['nome'] = r[0].strip()
            tbl.insert(record)
            d[record['nome']] = record['sigla']
    return d


def importCodici(db, filepath, d):
    tbl = db.table('glbl.nazione')
    f = file(filepath)
    t = f.read()
    lines = t.split('\n')
    for l in lines:
        if l:
            r = l.split(';')
            record = {}
            nome = r[0].strip()
            if nome in d.keys():
                record['sigla'] = d[nome].strip()
                record['codice_istat'] = r[1].strip()
                tbl.update(record)


if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/condox').db
    d = importSigleNaz(db, '/Users/saverioporcari/Desktop/sigle_naz.txt')
    importCodici(db, '/Users/saverioporcari/Desktop/codice_naz.txt', d)
    db.commit()

    print 'update done'
