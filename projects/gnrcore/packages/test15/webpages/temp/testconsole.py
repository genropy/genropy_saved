# -*- coding: utf-8 -*-

# bugsxml.py
# Created by Francesco Porcari on 2012-03-01.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
         
    def test_0_error(self,pane):
        pane.button('test',action="""
            FIRE .pippo;
        """)

        pane.dataController("""
        console.log('groupTreeData rebuild');
        var zz = k.m;
        console.log('after error');
        """,_fired='^.pippo')

    def test_2_th_store(self,pane):
        th = pane.plainTableHandler(table='glbl.provincia',height='300px')

        th.view.dataController("""
            console.log('groupTreeData rebuild');
            var zz = k.m;
            console.log('after error');
        """,gridstore='^.store',
        grid=th.view.grid.js_widget)