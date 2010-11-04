# -*- coding: UTF-8 -*-

# controllers.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""controllers"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """Params"""
        fb = pane.formbuilder(cols=2,border_spacing='4px',width='100px',fld_width='100%',datapath='test1')
        fb.numbertextbox(value='^.a',lbl='a')
        fb.numbertextbox(value='^.b',lbl='b')
        fb.dataFormula(".c","a+b",a="^.a",b='^.b')
        fb.div(value='^.c',lbl='a+b')
        
    def test_2_basic(self,pane):
        """Params"""
        fb = pane.formbuilder(cols=2,border_spacing='4px',width='100px',fld_width='100%',datapath='test2')
        fb.numbertextbox(value='^.a',lbl='a')
        fb.numbertextbox(value='^.b',lbl='b')
        fb.div(innerHTML='==a+b',a='^.a',b='^.b',lbl='a+b')
        
    def test_3_basic(self,pane):
        """Params"""
        # spiegare che la somma avviene al cambio di a, e non di b!
        fb = pane.formbuilder(cols=2,border_spacing='4px',width='100px',fld_width='100%',datapath='test3')
        fb.numbertextbox(value='^.a',lbl='a')
        fb.numbertextbox(value='^.b',lbl='b')
        fb.dataFormula(".c", "a+b",a="^.a",b='=.b')
        fb.div(value='^.c',lbl='a+b')
        
    def test_4_basic(self,pane):
        """Params"""
        fb = pane.formbuilder(cols=2,border_spacing='4px',width='100px',fld_width='100%',datapath='test4')
        fb.numbertextbox(value='^.a',lbl='a')
        fb.numbertextbox(value='^.b',lbl='b')
        fb.dataFormula(".c", "a+bquadro",a="^.a",b='^.b',bquadro='==b*b')
        fb.div(value='^.c',lbl='a+b^2')    