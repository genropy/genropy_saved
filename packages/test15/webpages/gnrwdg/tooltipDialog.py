# -*- coding: UTF-8 -*-

# connecteTooltipDialog.py
# Created by Francesco Porcari on 2011-03-18.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
   #def test_1_ddb(self,pane):
   #    """First test description"""
   #    t = pane.dropDownButton('test').tooltipDialog(title='Mario')
   #    t.div('ciao',height='300px',width='200px')
   #    #box.tooltipDialog(height='300px',width='400px',title='Mario')
   #    #box.ConnectedTooltipDialog(title='AAA')
    
    def test_2_div(self,pane):
        """First test description"""
        box = pane.div(height='30px',width='30px',background='red')
        t = box.tooltipDialog(title='Mario',modifiers='shift')
        t.div('ciao',height='300px',width='200px')
    
    def test_3_div(self,pane):
        t = pane.div(hidden=True).tooltipDialog(nodeId='pippo',evt='onclick',modifiers='shift')
        t.div('ciao',height='300px',width='200px')
        for color in ('red','green','blue'):
            pane.div(height='30px',width='30px',margin='50px',background=color,tooltipDialog='pippo')


