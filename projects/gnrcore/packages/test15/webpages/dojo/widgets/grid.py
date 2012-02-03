# -*- coding: UTF-8 -*-

# grid.py
# Created by Francesco Porcari on 2010-08-18.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Grid"""
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'
    
    def windowTitle(self):
        return 'Grid'
        

    def test_1_simple(self, root, **kwargs):
        root.div('ciao')
        root.includedView(storepath='grid.data', struct=self.gridStruct(),
                         autoWidth=True, splitter=True)
        root.dataRpc('grid.data', 'gridData', _fired='^gnr.onStart')

    def rpc_gridData(self):
        data = Bag()
        data.setItem('r1', None, name='Mark Smith', sex='M', birthday='1980-06-04::D', height=170)
        data.setItem('r2', None, name='Ann Brown', sex='F', birthday='1960-09-21::D', height=1730.45)
        return data

    def gridStruct(self):
        struct = Bag()
        r = struct.child('view').child('rows')
        r.child('cell', field='name', width='20em', name='Name')
        r.child('cell', field='sex', width='2em', name='Sex')
        r.child('cell', field='height', width='13em', name='Height', text_align='right',format_pattern='#.#', format_currency=False)
        r.child('cell', field='birthday', width='10em', name='Birthday', format_date='short')
        return struct
