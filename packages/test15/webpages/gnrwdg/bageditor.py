# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def windowTitle(self):
        return 'bageditor'
         
    def test_0_firsttest(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px',background='lime')
        bc.contentPane(region='top').button('load node',action='genro.publish("test_editnode","")')
        bc.contentPane(region='center').bagNodeEditor(bagpath='gnr',nodeId='test')
        