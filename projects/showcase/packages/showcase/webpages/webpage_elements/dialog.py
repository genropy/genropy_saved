# -*- coding: UTF-8 -*-

# dialog.py
# Created by Francesco Porcari on 2010-07-09.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dialog"""

class GnrCustomWebPage(object):
    py_requires = """foundation/dialogs,
                     gnrcomponents/testhandler:TestHandlerFull"""
                     
    def test_1_childname(self, pane):
        """simple dialog"""
        fb = pane.formbuilder(cols=2)
        fb.button('Open dialog', action="""SET mydialog.title = GET title;
                                           FIRE mydialog.open;""")
        fb.textbox(lbl='Dialog title',value='^title')
        dlg = self.simpleDialog(pane, dlgId='mydialog', height='200px', width='300px', title='^.title',
                                datapath='mydialog')