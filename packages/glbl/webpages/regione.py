#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  regione.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    maintable='glbl.regione'
    py_requires = 'public:Public,public:IncludedRecordView,standard_tables:TableHandler'
    
    def pageAuthTags(self, method=None, **kwargs):
        pass
        
    def tableWriteTags(self):
        pass
        
    def tableDeleteTags(self):
        pass
        
    def windowTitle(self):
        return '!!Regioni'
        
    def barTitle(self):
        return '!!Regioni'
        
    def columnsBase(self,):
        return """sigla:8,nome:8,ordine:12,zona:10"""
        
    def formBase2(self,parentBC,disabled=False,**kwargs):
        bc = parentBC.borderContainer(  **kwargs)
        fb = bc.contentPane(region='top', height='20ex', splitter=True).formbuilder(cols=2)
        fb.field('glbl.regione.sigla')
        fb.field('glbl.regione.nome')
        fb.field('glbl.regione.codice_istat')
        fb.field('glbl.regione.ordine')
        fb.field('glbl.regione.zona')
        
        center = bc.borderContainer(region='center')
        gridpane = center.contentPane(region='left', width='50%', splitter=True)
        recordBC = center.borderContainer(region='center')
        
        self.includedRecordPane(gridpane, gridId='provGrid', storepath='.@glbl_provincia_regione',
                                            struct=self._structProvinceGrid(),
                                            gridPars=dict(autoWidth=True),
                                            recordBC=recordBC, recordPaneCb=self.includedRegione)
                                            
    def formBase(self,parentBC,disabled=False,**kwargs):
        bc = parentBC.borderContainer(  **kwargs)
        pane = bc.contentPane(region='top', height='20ex', splitter=True)
        fb = pane.formbuilder(cols=2)
        fb.field('glbl.regione.sigla')
        fb.field('glbl.regione.nome')
        fb.field('glbl.regione.codice_istat')
        fb.field('glbl.regione.ordine')
        fb.field('glbl.regione.zona')
        
        gridpane = bc.borderContainer(region='center')
        
        self.includedRecordDialog(gridpane, gridId='provGrid', storepath='.@glbl_provincia_regione',
                                struct=self._structProvinceGrid(), 
                                gridPars=dict(autoWidth=True),
                                recordPaneCb=self.includedRegioneDialog
                                )
                                
    def includedRegioneDialog(self, parentDialog, **kwargs):
        bc = parentDialog.borderContainer(width='40em', height='40ex', **kwargs)
        self.includedRegione(bc)
        
    def includedRegione(self, parentBC, **kwargs):
        fb = parentBC.contentPane(**kwargs).formbuilder(cols=1)
        fb.div(lbl='selectedIndex', value='^grids.provGrid.selectedIndex')
        fb.div(lbl='selectedId', value='^grids.provGrid.selectedId')
        
        fb.field('glbl.provincia.sigla')
        fb.field('glbl.provincia.nome')
        fb.field('glbl.provincia.ordine')
        
    def _structProvinceGrid(self):
        struct = self.newGridStruct('glbl.provincia')
        r = struct.view().rows()
        r.fieldcell('sigla')
        r.fieldcell('nome')
        r.fieldcell('codice_istat')
        r.fieldcell('ordine')
        r.fieldcell('cap_valido')
        return struct
        
    def orderBase(self):
        return 'ordine'
        
    def queryBase(self):
        return dict(column='nome',op='startswith')
        