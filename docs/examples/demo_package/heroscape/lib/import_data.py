#!/usr/bin/env python
# encoding: utf-8
"""
import_data.py

Created by Saverio Porcari on 2008-03-07.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import md5
from gnr.app.gnrapp import GnrApp

def importGenerali(db):
    gen=db.table('heroscape.generale')
    gendict={'Aquilla':{'nome':'Aquilla','colore':'giallo'},'Einar':{'nome':'Einar','colore':'viola'},
       'Jandar':{'nome':'Jandar','colore':'azzurro'},'Ullar':{'nome':'Ullar','colore':'verde'},
       'Utgar':{'nome':'Utgar','colore':'rosso'},'Vydar':{'nome':'Vydar','colore':'grigio'}}
    for g in gendict.values():
        g['id']=gen.newPkeyValue()
        gen.insert(g)
    return gendict

def importTipi(db):
    tipodict={'Unique hero':{'nome':'Unique hero'},
              'Common hero':{'nome':'Common hero'},
              'Unique squad':{'nome':'Unique squad'},
              'Common squad':{'nome':'Common squad'}}
    
    tipo=db.table('heroscape.tipo')
    for t in tipodict.values():
        t['id']=tipo.newPkeyValue()
        tipo.insert(t)
    return tipodict
    

    
def importPersonaggi(db, gendict):
    unita=db.table('heroscape.unita')
    razzedict={}
    classdict={}
    persdict={}
    
    for k,v in gendict.items():
        path=os.path.join(os.getcwd(),'carte','%s.csv'%k)
        f=file(path)
        t=f.read()
        lines=t.split('\n')
        r_unita={}
        for l in lines:
            if l:
                r=l.split(',')
                x=r[0].split('(')
                if len(x)>1:
                    nome=x[0].strip()
                    numero=int(x[1].split(')')[0])
                else:
                    nome=r[0]
                    numero=1
                r_unita['id']=unita.newPkeyValue()
                r_unita['generale_id']=v['id']
                r_unita['nome']=nome
                r_unita['numero_miniature']=numero
                r_unita['costo_punti']=r[1]
                r_unita['mondo']=r[2]
                r_unita['razza_id']=getId(r[3], razzedict, 'razza')
                r_unita['classe_id']=getId(r[4], classdict, 'classe')
                r_unita['personalita_id']=getId(r[5], persdict, 'personalita')
                r_unita['dimensione']=r[6]
                r_unita['altezza']=int(r[7])
                r_unita['vite']=r[8]
                r_unita['movimento']=r[9]
                r_unita['gittata']=r[10]
                r_unita['attacco']=r[11]
                r_unita['difesa']=r[12]
                unita.insert(r_unita)
                
    for c in classdict.values():
        db.table('heroscape.classe').insert(c)
    for p in persdict.values():
        db.table('heroscape.personalita').insert(p)
    for r in razzedict.values():
        db.table('heroscape.razza').insert(r)
        

def getId(nome, dizionario, tblname):
    tbl=db.table('heroscape.%s' % tblname)
    record=dizionario.get(nome)
    if record:
         id=record['id']
    else:
        id=tbl.newPkeyValue()
        dizionario[nome]={'nome':nome, 'id':id}
    return id

if __name__ == '__main__':
    db=GnrApp('/usr/local/genro/data/instances/heroscape/').db
    gendict=importGenerali(db)
    importPersonaggi(db,gendict)
    importTipi(db)
    db.commit()
    c=0