# -*- coding: utf-8 -*-

# drop_uploader.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drop uploader"""

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    css_requires='public,bgfield'

    def test_1_pane(self, pane):
        bc = pane.borderContainer(height='400px',_class='mum')
        top = bc.contentPane(region='top',height='200px',_class='zzz')
        top.bagField(value='^.value',method=self.myhandler)
        bc.contentPane(region='center')
        
    def test_2_field(self, pane):
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top',height='50px',background='silver')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=2,lblpos='T')
        fb.bagField('^.alfa',lbl='Alfa')
        fb.bagField('^.beta',lbl='Beta')

    def test_3_field(self, pane):
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top',height='50px',background='silver')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=2,lblpos='T')
        fb.bagField('^.alfa',lbl='Alfa')
        fb.bagField('^.alfa_2',lbl='Alfa 2',field='alfa')

    def test_4_resource(self, pane):
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top',height='50px',background='silver')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=2,lblpos='T')
        fb.bagField('^.gamma',lbl='Gamma')
        fb.bagField('^.delta',lbl='Delta')

    @public_method
    def myhandler(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.foo',lbl='Foo')
        fb.textbox(value='^.bar',lbl='Bar')

    
    @public_method
    def bf_alfa(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.foo',lbl='Foo')
        fb.textbox(value='^.bar',lbl='Bar')

    @public_method
    def bf_beta(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.boo',lbl='Boo')
        fb.textbox(value='^.sob',lbl='Sob')