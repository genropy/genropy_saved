# -*- coding: UTF-8 -*-

# tooltipDialog.py
# Created by Francesco Porcari on 2011-03-18.
# Copyright (c) 2011 Softwell. All rights reserved.

"tooltipDialog"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source=True
    
    def windowTitle(self):
        return 'tooltipDialog'
         
    def test_1_tooltipPane(self,pane):
        """tooltipPane"""
        fb = pane.formbuilder(cols=2)
        dlg = fb.div(lbl='tooltipCode',height='40px',width='40px',
                     background='red').tooltipPane(tooltipCode='test1',evt='onclick')
        fb.div("""Click on the red div here to the left to open a tooltipPane.
                  By default, you can open a tooltipPane with an \'onClick\' event,
                  but you can modify the command to open the Pane through the \'evt\'
                  attribute (e.g: evt=\'ondblclick\'; e.g: evt=\'onmouseover\' ...)""")
        dlg.div(height='300px',width='400px')
        fb.div(lbl='standard_tooltip',height='40px',width='40px',
               background='teal',tooltip='This is a standard tooltip')
        fb.div("Move your mouse on the teal div to show a simple tooltip (no modifies on style).")
        fb.div(lbl='custom_tooltip',height='40px',width='40px',
               background='blue').tooltip("""<div style='height:60px;width:250px;color:teal;font-size:18px;'>
                                                 Here we modify the style!
                                             </div>""")
        fb.div("Move you mouse on the blue div to show a dialog with modified style.")
        
    def test_2_div(self,pane):
        """div tooltipPane"""
        pane.div("""You can open a tooltipPane in the red and the green div with a double click
                    (\'onDblClick\' event). The textboxes of the red and the green dialog are
                    linked with a remote call. The yellow div doesn\'t support any kind of action.""",
                    margin_left='15px',margin_top='10px')
        t = pane.tooltipPane(nodeId='pippo',evt='ondblclick',
                             onOpening="""if (sourceNode.attr.device){FIRE build = sourceNode.attr;
                                                                      return true;
                                                                      }
                                                                      """)
        t.div(height='200px',width='300px',rounded='10',
                    shadow='2px 2px 4px navy').remote('contenuto_test',attrs='^build')
                    
        pane.div(height='30px',width='30px',margin='10px',background='red',device='A.B')
        pane.div(height='30px',width='30px',margin='10px',background='yellow')
        pane.div(height='30px',width='30px',margin='10px',background='green',device='A.C')
        
    def remote_contenuto_test(self,pane,attrs=None):
        fb = pane.formbuilder(background=attrs['background'])
        fb.textbox(value='^campo1',lbl='Campo1')
        fb.textbox(value='^campo2',lbl='Campo2')
        fb.button(attrs['device'])