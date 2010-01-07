#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime
from gnr.core.gnrbag import Bag

import time

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)

        split=root.splitContainer(height='100%')
        left=split.contentPane(sizeShare=25,background_color='silver')
        
        left.tree(storepath='*D',inspect='shift',selected='datatree.selection',label="Data inspector")
        
        rightsplit=split.splitContainer(sizeShare=75,orientation='vertical')
        topright=rightsplit.contentPane(sizeShare=25)
        bottomright=rightsplit.contentPane(sizeShare=75)
        fb=topright.formbuilder(cols=2)
        fb.textbox(lbl='Cerca rag soc', value='^grid.cerca')
        fb.textbox(lbl='RagSoc Label', value='^ragsoc_label')
        fb.checkbox(lbl='Auto Width', value='^grid.autowidth')
        bottomright.dataRpc('grid.structure', "gridStructure", viewname='^ragsoc_label', _init=True)
        bottomright.dataSelection('grid.data','utils.anagrafiche',
                             columns='an_ragione_sociale,an_indirizzo,an_localita,an_cap,an_provincia',
                             where="an_ragione_sociale ILIKE :ragsoc",
                             ragsoc='^grid.cerca',
                             selectionName='mygrid')
                             
        mygrid=bottomright.grid(gnrId='mygrid',model='^grid.data',structure="^grid.structure", autoWidth='^grid.autowidth')
                              
    def rpc_gridStructure(self, viewname=None):
        b = Bag()
        if not viewname:
            view = b.child('view', childname='base')
            r = view.child('row', childname='base')
            r.child('cell', childname='ragsoc', name='Ragione Sociale',field='an_ragione_sociale')
            r.child('cell', name='Indirizzo' ,field='an_indirizzo')
            r.child('cell', name='Localita',field='an_localita')
            r.child('cell', name='Cap',field='an_cap')
            r.child('cell', name='Pr.',field='an_provincia')
        else:
            view = b.child('view', childname='base')
            r = view.child('row', childname='base')
            r.child('cell', childname='ragsoc', name=viewname, width='200px' ,field='an_ragione_sociale')
            r.child('cell', name='Indirizzo', width='200px' ,field='an_indirizzo')
            
            r = view.child('row', childname='bis')
            r.child('cell', name='Localita', width='200px' ,field='an_localita')
            r.child('cell', name='Cap', width='60px' ,field='an_cap')
            r.child('cell', name='Pr.', width='200px' ,field='an_provincia')
        return b
    
            
    
