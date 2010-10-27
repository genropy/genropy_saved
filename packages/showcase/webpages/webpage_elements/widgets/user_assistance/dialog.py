# -*- coding: UTF-8 -*-

# dialog.py
# Created by Francesco Porcari on 2010-07-09.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='foundation/dialogs'
    css_requires='public'
    css_theme='aqua'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main(self, root, **kwargs):
        root.button('Open',action='SET mydialog.title = GET title; FIRE mydialog.open;')
        root.textbox(value='^title')
        dlg = self.simpleDialog(root,dlgId='mydialog',height='200px',width='300px',title='^.title',datapath='mydialog')
