# -*- coding: utf-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-10-20.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"

    def test_0_a(self,pane):
        """Depending sections"""
        bc = pane.borderContainer(height='1000px')
        bc.contentPane(region='top',height='400px').plainTableHandler(table='glbl.comune',datapath='.topth',
                                                                        viewResource='View',extendedQuery=True,
                                                                                            virtualStore=True,
                                                                                            nodeId='topth',export=True)

