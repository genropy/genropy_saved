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

def importUtente(db, c):
    tbl = db.table('assopy.utente')
    record = {}
    idutente = tbl.newPkeyValue()
    record['id'] = idutente
    record['nome_cognome'] = c['ragione_sociale'][:31]
    #record['username']=c['ragione_sociale'].lower().replace(' ','_')[:31]
    record['username']=idutente
    #record['password']=str(random.random()*100000).replace('.','')[0:4]
    #record['pwd'] = md5.md5(record['password']).hexdigest()
    record['data_registrazione']=datetime.date.today()
    record['email']=c['email']
    tbl.insert(record)
    return idutente
    

def importAnagrafica(db, c, idutente):
    tbl=db.table('assopy.anagrafica')
    record={}
    idanagrafica = tbl.newPkeyValue()
    record['id'] = idanagrafica
    record['ragione_sociale']=c['ragione_sociale']
    record['codice_fiscale']=c['codice_fiscale']
    record['titolo']=c['titolo']
    record['partita_iva']=c['partita_iva']
    record['indirizzo']=c['indirizzo']
    record['localita']=c['localita']
    record['provincia']=c['provincia']
    record['cap']=c['cap']
    record['nazione']=c['nazione']
    record['ut_anagrafiche_id']=c['ut_anagrafiche_id']
    record['utente_id'] = idutente
    tbl.insert(record)
    return idanagrafica

def updateAnagraficaClienti(db, c):
    tbl=db.table('assopy.anagrafica')
    record={'id':c['id'],
            'coge_id':c['coge_id'],
            'tipo_cliente':c['tipo_cliente'],
            'tipo_iva':c['tipo_iva'],
            'cond_pagamento':c['cond_pagamento']}
    tbl.update(record)
    


if __name__ == '__main__':
    db = GnrApp('/usr/local/genro/data/instances/assopy').db
    t=db.packages['tools']
    an=db.table('assopy.anagrafica').model
    z=an.relatingColumns
    old_anagrafiche=db.query('utils.anagrafiche',columns="""$sy_id,
                                                   $sy_id AS ut_anagrafiche_id,
                                                   $an_ragione_sociale AS ragione_sociale,
                                                   $an_indirizzo AS indirizzo,
                                                   $an_cap AS cap,
                                                   $an_localita AS localita,
                                                   $an_provincia AS provincia,
                                                   $an_nazione AS nazione,
                                                   $an_titolo AS titolo,
                                                   $ds_codice_fiscale AS codice_fiscale,
                                                   $ds_partita_iva AS partita_iva,
                                                   $tc_email AS email
                                                   """).fetch()

    
    for c in old_anagrafiche:
        idutente = importUtente(db,c)
        idanagrafica = importAnagrafica(db,c, idutente)
    db.commit()
    print 'import done'            
    old_clienti=db.query('coge.clienti',
                          columns="""$sy_id AS coge_id,
                                     $cg_tipo_cliente AS tipo_cliente,
                                     $cg_tipo_iva AS tipo_iva,
                                     $cg_condizioni_pagamento AS cond_pagamento,
                                     @sy_id_anagrafiche.@assopy_anagrafica_ut_anagrafiche_id.id AS id""").fetch()
    for c in old_clienti:
        updateAnagraficaClienti(db,c)                                                 
    db.commit()
    
    print 'update done'
