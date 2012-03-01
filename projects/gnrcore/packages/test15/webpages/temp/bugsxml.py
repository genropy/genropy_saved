# -*- coding: UTF-8 -*-

# bugsxml.py
# Created by Francesco Porcari on 2012-03-01.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
         
    def test_0_dataxml(self,pane):
        """First test description"""
        pane.dataRpc('prova',self.recordInAttribute,_onStart=True)
    
    @public_method
    def recordInAttribute(self):
        return 'zzz',dict(_record=dict(self.db.table('polimed.medico').record(pkey='qYIlia6_NxmnnR0JwcIuTA').output('dict')))