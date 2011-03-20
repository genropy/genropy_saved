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
        pane.script("""
        
        dojo.connect(dijit,'_place',function(){
            console.log(arguments);
        });
        """)
        dlg = pane.div(height='40px',width='40px',background='red').tooltipPane(tooltipCode='test1')
        dlg.div(height='300px',width='400px')
        pane.div(height='40px',width='40px',background='blue').tooltip("<div style='height:300px;width:200px;'>ciao</div>")
        
   #def test_1_ddb(self,pane):
   #    """First test description"""
   #    t = pane.dropDownButton('test').tooltipDialog(title='Mario')
   #    t.div('ciao',height='300px',width='200px')
   #    #box.tooltipDialog(height='300px',width='400px',title='Mario')
   #    #box.ConnectedTooltipDialog(title='AAA')
    
   #def test_2_div(self,pane):
   #    """First test description"""
   #    box = pane.div(height='30px',width='30px',background='red')
   #    t = box.tooltipDialog(title='Mario',modifiers='shift')
   #    t.div('ciao',height='300px',width='200px')
   #
    def test_3_div(self,pane):
        #pane.attributes['_class'] = 'xxxx'
        t = pane.tooltipPane(nodeId='pippo',evt='onclick',modifiers='shift',onOpening='return sourceNode.attr.connected;')
        t.div('ciao',height='100px',width='200px')
        for color in ('red','green','blue'):
            pane.div(height='30px',width='30px',margin='50px',background=color,connected=True)
    

