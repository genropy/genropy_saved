# -*- coding: utf-8 -*-

# dashboards gallery.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="""public:Public,th/th:TableHandler"""

    def main(self,root,**kwargs):
        root = root.rootContentPane(title='!!Legacy converter editor',datapath='main',**kwargs)
        root.dialogTableHandler(table='lgcy.converter',viewResource='ConverterEditorView',
                                formResource='ConverterEditorForm',
                                view_store__onStart=True)