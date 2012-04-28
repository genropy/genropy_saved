# -*- coding: UTF-8 -*-

# tooltipDialog.py
# Created by Francesco Porcari on 2011-03-18.
# Copyright (c) 2011 Softwell. All rights reserved.

"tooltipDialog"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source=True
    
    def windowTitle(self):
        return 'ComboArrow'
         
    def test_1_Menu(self,pane):
        """tooltipPane"""
        fb = pane.formbuilder(cols=2)
        fb.textbox(value='^.val', lbl='Choose Value',position='relative').comboMenu(values='Pippo,Pluto,Paperino',_class='smallmenu')
    
    def test_1_Tooltip(self,pane):
        """tooltipPane"""
        fb = pane.formbuilder(cols=2)
        tooltip = fb.textbox(value='^.val', lbl='Choose Value',position='relative').comboArrow().tooltipPane()
        tooltip.div('Ciao come va?',height='100px',width='200px')