#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Formula examples """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        
        split = root.splitContainer(height='100%')
        left = split.contentPane(sizeShare=20)
        left.tree(store_path="*D", inspect='shift', label='Dati')
        
        rsplit = split.splitContainer(sizeShare=80, orientation='vertical')
        rtop = rsplit.contentPane(sizeShare=20)
        rbottom = rsplit.contentPane(sizeShare=80)
        
        fb = rtop.formbuilder(cellspacing=10, cols=2)
        fb.numberSpinner(lbl='page', datasource='panes.selected', intermediateChanges=True)
        
        tab = rbottom.tabContainer(height='100%', datasource='panes', selected='@panes.selected', default_selected=1)
        self.tabFormule(tab)
        self.tabDbSelect(tab)
        self.tabSelection(tab)
        
    def tabFormule(self, where):
        pane = where.contentPane(title='formule', datasource=':formule')
        
        fb = pane.formbuilder(cols=2, cellspacing=10, lblpos='T', datasource=':triangolo')
        fb.data(':base', 10)
        fb.data(':altezza', 0)
        fb.dataFormula(':area', 'b * h / 2', b='@:base', h='@:altezza')
        fb.dataRpc(':controllo', 'controlloArea', area='@:area')
        
        fb.numberTextBox(lbl='Base' , lbl_color='red', datasource=':base')
        fb.numberTextBox(lbl='Altezza', datasource=':altezza')
        fb.div(lbl='Area', datasource=':area', border='1px solid grey')
        fb.div(lbl='Controllo', datasource=':controllo', border='1px solid grey')
        
    def tabDbSelect(self, where):
        pane = where.contentPane(title='dbselect', datasource=':dbselect')
        
        lc = pane.layoutContainer(height='100%')
        fb = lc.contentPane(layoutAlign='top', height='5.5em').formbuilder(cols=2, cellspacing=10, datasource=':prov')
        
        fb.dataRecord(':record', 'utils.province', pkey='@:codice')
        
        fb.dbSelect(lbl='Provincia', datasource = ':codice',ignoreCase=True,
                               dbtable='utils.province',columns='descrizione',
                               method='dbSelect')
        
        fb.dbSelect(lbl='Anagrafica',ignoreCase=True,
                               dbtable='utils.anagrafiche',columns='$an_ragione_sociale, $an_localita', 
                               auxColumns='$an_provincia,@an_provincia.@regione.descrizione as regione',
                               method='dbSelect')
        

        fb.div(datasource=':record.@regione.codice')
        
        cli = lc.contentPane(layoutAlign='client')
        tab = cli.tabContainer(height='100%')
        pr = tab.contentPane(title='Province')
        pr.grid(model='@panes.dbselect.prov.record.@regione.@utils_province_regione.data', structure='@panes.dbselect.prov.record.@regione.@utils_province_regione.structure')
        
        pr = tab.contentPane(title='Anagrafiche')
        pr.dataSelection('selection', table='utils.anagrafiche', where='an_provincia = :prov', prov='@:prov.codice', structure=True,
                     columns='$an_ragione_sociale, $an_localita, $an_cap')
        pr.grid(model='@selection.data', structure='@selection.structure')

    def tabSelection(self, where):
        pane = where.contentPane(title='selection', datasource=':selection')
        


    def rpc_controlloArea(self, area):
        area = float(area)
        if area > 100:
            return "troppo grande"
        elif area < 10:
            return "troppo piccola"
        else:
            return "Bella"
        
        


