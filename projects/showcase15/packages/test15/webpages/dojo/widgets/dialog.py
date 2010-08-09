# -*- coding: UTF-8 -*-
# 
"""Dialogs"""

class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerBase"
    dojo_theme='claro'
    
    def test_1_basic(self,pane):
        """Basic Dialog"""
        dlg=pane.dialog(nodeId='mydialog',style='width:300px;',title='Very simple dialog')
        dlg.div('This is a very simple dialog')
        pane.button('Open a dialog',action="genro.wdgById('mydialog').show()")
        
    def test_2_nested(self,pane):
        """Nested Dialogs"""
        x=100
        y=100
        for k in range (4):
            dlg=pane.dialog(nodeId='mydialog_%i' % k,style='width:300px;',
                            title='Very simple dialog n. %i'%k,position='%i,%i'%(x,y))
            dlg.div('This is a very simple dialog %i' %k)
            pane.button('Open a dialog %i'%k,action="genro.wdgById('mydialog_%i').show()" %k)
            pane=dlg
            
    def test_3_variable_title(self,pane):
        """Dialog with variable title"""

        dlg=pane.dialog(nodeId='mydialog_variable_title',duration=1000,
                       style='width:300px;top:20px;',title='^dialogTitle')
        dlg.div('This is dialog with a variable title')
        dlg.hr()
        fld=dlg.div()
        fld.span('dialog title : ')
        fld.span().textbox(value='^dialogTitle',placeholder='dialog title')
        pane.data('dialogTitle','dialog title')
        pane.button('Open a dialog',action="genro.wdgById('mydialog_variable_title').show()")

