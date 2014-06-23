# -*- coding: UTF-8 -*-

# bugsxml.py
# Created by Francesco Porcari on 2012-03-01.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
         
    def test_0_smartscroll(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.data('.height',50)
        fb.data('.width',200)

        fb.numberTextBox(value='^.height',lbl='height')
        fb.horizontalSlider(value='^.width',lbl='width',width='19em',minimum=100, maximum=1000,
                            intermediateChanges=True)

        box = pane.div(height='100px',width='300px',overflow='hidden',border='1px solid silver',margin='10px',nodeId='xxx')
        d = box.div(display='inline-block',nodeId='yyy').div(height='==_h+"px";',_h='^.height',width='==_w+"px";',_w='^.width',background='lightgreen',
                border='1px solid darkgreen',
                margin='2px')
        d.span('This Is A Test',font_size='14pt')
        pane.dataController("""
             setInterval(function(){
                var envelope = box.firstChild;
                     var deltascroll_w = envelope.clientWidth - box.clientWidth;
                     var deltascroll_h = envelope.clientHeight - box.clientHeight;
                     if(deltascroll_w>0){
                        var z_a =box.clientWidth/ envelope.clientWidth;
                        //console.log('clientWidth',box.clientWidth, 'scrollWidth',box.scrollWidth ,'zoom a',z_a)
                        envelope.style.zoom = z_a;
                     }
                 },50);

         """,_onStart=True,box=box.js_domNode,d=d.js_domNode)

    def test_1_zoomToFit(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.data('.height',50)
        fb.data('.width',200)

        fb.numberTextBox(value='^.height',lbl='height')
        fb.horizontalSlider(value='^.width',lbl='width',width='19em',minimum=100, maximum=1000,
                            intermediateChanges=True)
        box = pane.div(height='100px',width='300px',overflow='hidden',border='1px solid silver',margin='10px',zoomToFit='x')
        d = box.div(height='==_h+"px";',_h='^.height',width='==_w+"px";',_w='^.width',background='lightgreen',
                border='1px solid darkgreen',
                margin='2px')
        d.span('This Is A Test',font_size='14pt')

    def test_2_zoomToFitMulti(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.data('.buttons','P:Pippo,B:Buzzo')
        fb.textbox(value='^.buttons',lbl='Buttons')
        #box = pane.div(width='300px',overflow='hidden',xborder='1px solid silver',margin='10px',zoomToFit='x')
        pane.multibutton(value='^.pippero',values='^.buttons',white_space='nowrap',width='300px',zoomToFit='x',border='1px solid green')




