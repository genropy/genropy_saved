# -*- coding: UTF-8 -*-

# thlight.py
# Created by Francesco Porcari on 2011-03-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
    auto_polling=0
    user_polling=0
    def test_0_localita(self,pane):
        """First test description"""
        th = pane.borderContainer(height='400px').plainTableHandler(table='glbl.provincia',region='center',viewResource=':EditableView')
        th.view.store.attributes.update(_onStart=True,recordResolver=False)
       #ge = th.view.grid.gridEditor()
       #ge.textbox(gridcell='nome')