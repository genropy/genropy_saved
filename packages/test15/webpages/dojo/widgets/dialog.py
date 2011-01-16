# -*- coding: UTF-8 -*-
# 
"""Dialogs"""

class GnrCustomWebPage(object):
    dojo_version = '11'
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    css_theme = 'aqua'
    css_requires='public'
    dojo_theme = 'tundra'

    def test_1_basic(self, pane):
        """Basic Dialog"""
        dlg = pane.dialog(nodeId='mydialog', style='width:300px;', title='Very simple dialog')
        dlg.div('This is a very simple dialog')
        pane.button('Open a dialog', action="genro.wdgById('mydialog').show()")
        pane.div(height='40px').palettePane('pippo',title='pippo',dockTo='*')

    def test_2_nested(self, pane):
        """Nested Dialogs"""
        for k in range(4):
            dlg = pane.dialog(nodeId='mydialog_%i' % k, style='width:300px;',
                              title='Very simple dialog n. %i' % k, position='%i,%i' % (100 + k * 10, 100 + k * 10))
            dlg.div('This is a very simple dialog %i' % k)
            pane.button('Open a dialog %i' % k, action="genro.wdgById('mydialog_%i').show()" % k)
            pane = dlg

    def test_3_variable_title(self, pane):
        """Dialog with variable title"""
        dlg = pane.dialog(nodeId='mydialog_variable_title', duration=1000,
                          style='width:300px;top:20px;', title='^dialogTitle')
        dlg.div('This is dialog with a variable title')
        dlg.hr()
        fld = dlg.div()
        fld.span('dialog title : ')
        fld.span().textbox(value='^dialogTitle', placeholder='dialog title')
        pane.data('dialogTitle', 'dialog title')
        pane.button('Open a dialog', action="genro.wdgById('mydialog_variable_title').show()")

    def test_4_tooltip_dialog_in_dialog(self, pane):
        pane.button('show', action='genro.wdgById("mydialog_with_tooltip").show();')
        dlg = pane.dialog(nodeId='mydialog_with_tooltip', duration=1000,
                          style='width:300px;top:20px;', title='^dialogTitle')
        box = dlg.div(height='300px', width='400px')
        innerdlg = box.dropDownButton('open tooltip').tooltipDialog(title='inner dialog')
        innerbox = innerdlg.div(height='150px', width='200px')
        fb = innerbox.formbuilder(cols=1, border_spacing='2px')
        fb.textbox(value='^aaa', lbl='Try')
        fb.textbox(value='^bb', lbl='Try 2')


