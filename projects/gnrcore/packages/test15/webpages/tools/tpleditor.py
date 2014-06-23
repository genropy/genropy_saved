# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:TemplateEditor"
    
    def test_0_dbstore(self,pane):
        """First test description"""
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=2, border_spacing='0')
        fb.textbox(value='^.table',lbl='Maintable')
        te=bc.contentPane(region='center').templateEditor(value='^.tplbag',maintable='^.table')
        te.store.......
        
    def test_1_doc(self,pane):
        """First test description"""
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=2, border_spacing='0')
        bc.contentPane(region='center').templateEditor(maintable='^.table',path='')

    def test_2_resource(self,pane):
        """First test description"""
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=2, border_spacing='0')
        bc.contentPane(region='center').templateEditor(maintable='^.table',resource_name='')

