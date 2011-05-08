# -*- coding: UTF-8 -*-

# genrodlg.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""genrodlg"""

import os
from gnr.core.gnrbag import Bag
import random
import time

cli_max = 12
invoice_max = 20
row_max = 100
sleep_time = 0.05

class GnrCustomWebPage(object):
    dojo_version = '11'
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'Test warning and ask'

    def test_1_ask(self, pane):
        "Batch"
        pane.button(action="FIRE .savingCommand='.saveAndClose'", label='Save and close')
        pane.button(action="FIRE .savingCommand='.saveAndAdd'", label='Save and new')
        pane.dataController("""
                            var _this = this;
                            var cb = function(){_this.fireEvent(savingCommand);}
                            genro.dlg.ask("Warning",
                                                 "This job has zero amount, proceed anyway?",
                                                  {'cancel':'Cancel', 'continue':'Continue'},
                                                  {'continue': cb});
                            """, savingCommand='^.savingCommand')
        pane.dataController("""alert('saveAndClose')""", fire='^.saveAndClose')
        pane.dataController("""alert('saveAndAdd')""", fire='^.saveAndAdd')