# -*- coding: UTF-8 -*-

# thlight.py
# Created by Francesco Porcari on 2011-03-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,tablehandler/th_components:StackTableHandler"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.localita',inputForm='thform/default')
        sc.form.store.handler('load',default_provincia='MI')