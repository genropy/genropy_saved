# -*- coding: UTF-8 -*-
"""includedview"""

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_simple(self, pane):
        """includedview - js widget"""
        pane = pane.contentPane(height='80px')
        pane.includedView(storepath='.grid.data', struct=self.gridStruct(), splitter=True)
        pane.dataRpc('.grid.data', self.gridData, _onStart=True)
        
    @public_method
    def gridData(self):
        data = Bag()
        data.setItem('r1', None, name='Mark Smith', sex='M', birthday='1980-06-04::D', height=170)
        data.setItem('r2', None, name='Ann Brown', sex='F', birthday='1960-09-21::D', height=1730.45)
        return data
        
    def gridStruct(self):
        struct = Bag()
        r = struct.child('view').child('rows')
        r.child('cell', field='name', width='100%', name='Name')
        r.child('cell', field='sex', width='4em', name='Sex')
        r.child('cell', field='height', width='10em', name='Height', text_align='right')
        r.child('cell', field='birthday', width='10em', name='Birthday', format_date='short')
        return struct