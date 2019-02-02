#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#  Created by Francesco Porcari
#
from gnr.core.gnrbag import Bag

def getSyncTables(db,filterstring=None,multidbMode=None):
    filterstring = filterstring or ''
    result = Bag()
    for pkgobj in list(db.packages.values()):
        for tableobj in list(pkgobj.tables.values()):
            tblattr = tableobj.attributes
            tablename = tableobj.fullname
            if tblattr.get('multidb') and filterstring in tablename:
                multidb='complete' if tblattr['multidb']=='*' else 'partial'
                if multidbMode and multidb!=multidbMode:
                    continue
                result.setItem('%s_%s' %(pkgobj.name,tableobj.name),None,caption=tablename,
                    multidb=multidb,
                    tablename=tablename,
                    _pkey=tablename)
    return result