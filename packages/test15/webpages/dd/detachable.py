# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.
# 


"""Test drag & drop detachable pane"""

class GnrCustomWebPage(object):

    py_requires="""gnrcomponents/testhandler:TestHandlerFull"""
    def test_0_tabContainer(self,pane):
        """Drop Boxes"""
        tc=pane.tabContainer(height='300px',width='200px')
        one=tc.contentPane(title='One').contentPane(background_color='pink',detachable=True)
        one.div('one')
        one.div('pippo',background='blue')
        two=tc.contentPane(title='Two',background_color='yellow')
        two.div('two',draggable=True)
        three=tc.contentPane(title='Three',background_color='lime')
        three.div('three')

    