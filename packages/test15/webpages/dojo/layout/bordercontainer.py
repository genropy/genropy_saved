# -*- coding: UTF-8 -*-

# bordercontainer.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""bordercontainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    #dojo_theme = 'claro'
    
    def windowTitle(self):
        return 'borderContainer'
        
    def test_bordercontainer_inside_cb(self, pane):
        bc = pane.contentPane(height='200px',background='green').borderContainer(background='red')
        
    def test_bordercontainer_cb_splitter(self, pane):
        bc = pane.borderContainer(height='200px')
        bc.contentPane(region='left',width='500px',splitter=True,background='lime').contentPane().remote('xxx',_fired='^aaa')
        bc.contentPane(region='center')
        
    def remote_xxx(self,pane,**kwargs):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        fb.textbox(lbl='aaa')
        fb.textbox(lbl='bbb')
        
    def test_bordercontainer_inside_cb_2(self, pane):
        bc = pane.tabContainer(height='200px',background='green')
        bc.contentPane(background='red',title='aa').borderContainer(background='pink')
        
    def _test_bordercontainer_mixedlayout(self, pane):
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='top', height='20px', background='red', splitter=True)
        tc = bc.tabContainer(region='left', width='400px')
        tc.contentPane(title='aa')
        tc.contentPane(title='bb')
        ac = bc.accordionContainer(region='right', width='400px')
        bc2 = ac.borderContainer(title='aa', background='black')
        bc2.contentPane(region='bottom', height='30px', background='silver')
        bc2.contentPane(region='center', background='lime')
        ac.contentPane(title='bb')
        bc.contentPane(region='center', background='yellow')
        
class ToFix(object):
    """we have to add regions in genroway"""
    
class FixedToCheck(object):
    """
    """
    
class Fixed(object):
    """docstring for Fixed"""
        