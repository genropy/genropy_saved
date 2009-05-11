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

def importSocio(db, c):
    tbl = db.table('assopy.socio')
    record = {}
    record['id'] = tbl.newPkeyValue()
    if c['nome']:
        record['nome_cognome'] = c['nome'][:31]
        record['descrizione'] = c['descrizione']
        record['anagrafica_id']=c['anag_id']
    else:
        print c['descrizione']
    tbl.insert(record)

if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/assopy').db
    old_soci=db.query('coge.piano_conti',
                      columns="""$descrizione,
                                 $codice,
                                 $sy_id_anagrafiche,
                                 @sy_id_anagrafiche.@assopy_anagrafica_ut_anagrafiche_id.id AS anag_id,
                                 @sy_id_anagrafiche.@assopy_anagrafica_ut_anagrafiche_id.ragione_sociale AS nome""",
                      where='$codice ILIKE :cod',cod='08.01.%').fetch()
    
    for c in old_soci:
        importSocio(db,c)

    db.commit()
    print 'done'
