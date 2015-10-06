# -*- coding: UTF-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 10
    user_polling = 3

    def test_0_tree(self, pane):
        pane.dataRemote('.store',self.relationExplorer,table='glbl.provincia',currRecordPath='record')
        pane.tree('.store',hideValues=True)
