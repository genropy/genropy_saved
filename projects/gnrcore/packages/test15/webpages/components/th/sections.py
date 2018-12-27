# -*- coding: utf-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-10-20.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"

    def test_0_depending_sections(self,pane):
        """Depending sections"""
        pane.borderContainer(height='500px').contentPane(region='center').plainTableHandler(table='glbl.provincia',
                                                                                            viewResource='ViewTestSections',condition_onStart=True)