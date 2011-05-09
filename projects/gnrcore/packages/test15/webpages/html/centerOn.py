#!/usr/bin/python
# -*- coding: utf-8 -*-

"genro.dom.centerOn"

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'
    
    def test_1_parentContentPane(self, pane):
        "genro.dom.centerOn('test1')"
        pane.button('Center', action="genro.dom.centerOn('test1')")
        cp = pane.div(height="300px", width="300px", background_color="lime", position="relative")
        cp.div('prova', width="100px", height="100px", id="test1", background_color="white", position="absolute")
        
    def test_2_parentWhere(self,pane):
        "genro.dom.centerOn('test2a','test2b') with test2b = test2a.parentNode"
        pane.button('Center', action="genro.dom.centerOn('test2a','test2b')")
        cp = pane.div(height="300px", width="300px", background_color="lime", id="test2b")
        cp.div('prova', width="100px", height="100px", id="test2a", background_color="white", position="absolute")
        
    def _test_3_nonParentWhere(self,pane):
        "genro.dom.centerOn('test3a','test3b') with test3b != test3a.parentNode"
        pane.button('Center', action="genro.dom.centerOn('test3a','test3b')")
        cp = pane.div(height="300px", width="300px", background_color="lime", id="test3b")
#        pane.div('prova', width="100px", height="100px", id="test3a", background_color="white", position="absolute")
        