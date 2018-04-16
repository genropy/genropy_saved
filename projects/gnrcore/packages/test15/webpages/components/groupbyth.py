# -*- coding: UTF-8 -*-

# genrodlg.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""genrodlg"""

import os
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    dojo_version = '11'
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"


    def test_0_dashboard(self, pane):
        pane.groupByTableHandler(table='fatt.fattura',height='400px',width='600px',
                                dashboardIdentifier='per_zona',configurable=False)
