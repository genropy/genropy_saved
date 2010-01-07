#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os, datetime

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self, root, **kwargs):
        root, top, bottom = self.pbl_rootTabContainer(root)
        
        t1 = root.contentPane()
        t1.data('mycontext', context='mycontext')
        
        t1.dbSelect(dbtable='glbl.regione', value='^regione_id')
        t1.textbox(value='^mycontext.lettera')
        
        t1.dataRecord('regione', 'glbl.regione', pkey='^regione_id', sqlContextName='ctxregione')
        self.setJoinCondition('ctxregione', from_fld='glbl.regione.sigla', target_fld='glbl.provincia.regione', 
                                condition='$tbl.nome ILIKE :lettera', 
                                lettera='^mycontext.lettera')
                                
        grid = t1.div(width='100%', height='300px').IncludedView(struct=self._gridStruct(), 
                        storepath='regione.@glbl_provincia_regione')
                     

        t2 = root.contentPane()
        t2.textbox(value='^mycontext.lettera')
        t2.dataSelection('lista_regioni', 'glbl.regione', sqlContextName='ctxregione2', _fired='^mycontext.lettera', 
                                           columnsFromView='lista_regioni')

        self.setJoinCondition('ctxregione2', 
                                condition='$tbl.nome ILIKE :lettera', 
                                lettera='^mycontext.lettera')
                                
        self.setJoinCondition('ctxregione2', from_fld='glbl.regione.sigla', target_fld='glbl.provincia.regione', 
                                condition='$tbl.nome ILIKE :lettera', 
                                lettera='^mycontext.lettera')
                                
        grid = t2.div(width='100%', height='300px').IncludedView(struct=self._gridStruct2(), 
                        storepath='lista_regioni')
                                
    def _gridStruct(self):
        struct = self.newGridStruct('glbl.provincia')
        r = struct.view().rows()
        r.fieldcell('sigla')
        r.fieldcell('nome')
        return struct
            
    def _gridStruct2(self):
        struct = self.newGridStruct('glbl.regione')
        r = struct.view().rows()
        r.fieldcell('sigla')
        r.fieldcell('nome')
        r.fieldcell('@glbl_provincia_regione.nome')
        return struct

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
