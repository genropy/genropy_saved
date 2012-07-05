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
        pane.dataRecord('record','studio.pt_uscita',default_tipo_id='1-KC7vGDM_u55MEOpv47Dg',pkey='*newrecord*',_onStart=True,ignoreMissing=True)
        pane.dataRemote('.store',self.relationExplorer,table='studio.pt_uscita',currRecordPath='record')
        pane.tree('.store',hideValues=True)
