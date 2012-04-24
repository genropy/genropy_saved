# -*- coding: UTF-8 -*-

# detachable.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drag & drop detachable pane"""

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    
    def test_0_tabContainer(self, pane):
        """Drop Boxes"""
        tc = pane.tabContainer(height='300px', width='400px')
        one = tc.contentPane(title='One').contentPane(background_color='pink', detachable=True)
        one.div('one')
        one.div('pippo', background='blue')
        two = tc.contentPane(title='Two').contentPane(background_color='yellow', detachable=True)
        two.div('two')
        three = tc.contentPane(title='Three').contentPane(background_color='lime', detachable=True)
        three.div('three')