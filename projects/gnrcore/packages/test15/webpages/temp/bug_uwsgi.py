# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

from datetime import datetime

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.button('run',fire='.run')
        fb.dbselect(value='^.pippo',dbtable='glbl.nazione',lbl='Naz')
        fb.div('^.result')
        fb.dataRpc('.result',self.getTimeStamp,_fired='^.run')

    @public_method
    def getTimeStamp(self):
        return datetime.now()



