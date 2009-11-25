#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class StatsHandler(BaseComponent):
    
    def stats_main(self,parent,**kwargs):
        """docstring for stats_mainpane"""
        bc = parent.borderContainer(**kwargs)
        top = bc.contentPane(region='top',height='30ex')
        left = bc.contentPane(region='left',width='300px',splitter=True)
        center = bc.borderContainer(region='center')
        self.stats_top(top)
        self.stats_left(left)
        self.stats_center(center)
    
    def stats_top(self,pane):
        pane.div('qui ci metto le ricerche')
    def stats_left(self,pane):
        pane.tree(storepath='.root',inspect='shift',selectedPath='.currentTreePath')
    def stats_center(self,bc):
        pass
        
    def analisi_prestazioni_tab___(self,bc):
        top = bc.contentPane(region='top',height='5ex',overflow='hidden').toolbar(height='5ex')
        left = bc.contentPane(region='left',width='30%',spitters=True)
        left.tree(storepath='.root',inspect='shift',selectedPath='.currentTreePath')
        left.dataRpc('.root.analisi','getAnalisi',period='^.period',medico_id='^form.record.id',_if='period')
        left.data('.root.analisi',Bag())
        self.analisi_prestazioni_grid(bc.borderContainer(region='center',margin='2px'))
        fb = top.formbuilder(cols=5,border_spacing='4px')
        self.periodCombo(fb,lbl='!!Periodo')