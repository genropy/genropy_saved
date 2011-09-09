# -*- coding: UTF-8 -*-

# macrowidgets.py
# Created by Filippo Astolfi on 2011-09-07.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Macrowidgets"""

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                     public:Public"""
                     
    def test_1_periodcombo(self, pane):
        """periodCombo"""
        pane = pane.contentPane(height='200px',datapath='periodCombo')
        fb = pane.formbuilder(cols=2)
        self.periodCombo(fb,lbl='!!Period',period_store='.period')
        fb.div(value='^.period.period_string', _class='period',font_size='.9em',font_style='italic')
        
    def test_2_selectionbrowser(self, pane):
        """selectionBrowser"""
        pane = pane.contentPane(height='200px',datapath='selectionBrowser')
        self.selectionBrowser(pane,rowcount=0,indexPath=0)
        pane.div('add??? Add a grid with rows and columns',margin='20px')