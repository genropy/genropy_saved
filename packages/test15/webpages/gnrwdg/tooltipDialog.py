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
         
    def _test_1_tooltipPane(self,pane):
        dlg = pane.div(height='40px',width='40px',background='red').tooltipPane(tooltipCode='test1')
        dlg.div(height='300px',width='400px')
        pane.div(height='40px',width='40px',background='blue').tooltip("<div style='height:300px;width:200px;'>ciao</div>")
        
   #
    def test_3_div(self,pane):
        t = pane.tooltipPane(nodeId='pippo',evt='ondblclick',onOpening="""
                                                                                        if (sourceNode.attr.device){
                                                                                            FIRE build = sourceNode.attr;
                                                                                            return true;
                                                                                        }
                                                                                    """)
        t.div(height='200px',width='300px',rounded='10',
                    shadow='2px 2px 4px navy').remote('contenuto_test',attrs='^build')

        
        pane.div(height='30px',width='30px',margin='10px',background='red',device='A.B')
        pane.div(height='30px',width='30px',margin='10px',background='yellow')
        pane.div(height='30px',width='30px',margin='10px',background='green',device='A.C')

    def remote_contenuto_test(self,pane,attrs=None):
        fb = pane.formbuilder(cols=1, border_spacing='2px',background=attrs['background'])
        fb.textbox(value='^campo1',lbl='Campo1')
        fb.textbox(value='^campo2',lbl='Campo2')
        fb.button(attrs['device'])
        