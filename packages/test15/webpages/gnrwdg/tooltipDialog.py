# -*- coding: UTF-8 -*-

# connecteTooltipDialog.py
# Created by Francesco Porcari on 2011-03-18.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source=True

    def windowTitle(self):
        return ''
         
    def test_1_tooltipPane(self,pane):
        dlg = pane.div(height='40px',width='40px',background='red').tooltipPane(tooltipCode='test1')
        dlg.div(height='300px',width='400px')
        pane.div(height='40px',width='40px',background='blue').tooltip("<div style='height:300px;width:200px;'>ciao</div>")
        
   #
    def test_3_div(self,pane):
        t = pane.tooltipPane(nodeId='pippo',evt='onclick',modifiers='shift',onOpening='return sourceNode.attr.miotipo=="pippo";')
        box = t.div(height='200px',width='300px',rounded='10',background='lime',shadow='2px 2px 4px navy')
        fb = box.formbuilder(cols=1, border_spacing='2px')
        fb.textbox(value='^campo1',lbl='Campo1')
        fb.textbox(value='^campo2',lbl='Campo2')
        fb.button('Vai')
        
        for color in ('red','green','blue'):
            pane.div(height='30px',width='30px',margin='50px',background=color,miotipo='pippo')
    

