#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Grid Test"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(height='100%')
        top = bc.contentPane(region='top', height='150px', overflow='hidden')
        top.span('local data from')
        top.includedView(storepath='grid.data', struct=self.gridStruct(),
                         autoWidth=True, splitter=True)

        center = bc.contentPane(region='center', overflow='hidden')
        center.span('local data from db')
        center.includedView(table='showcase.movie', columns='title,year,nationality',
                            storepath='grid.sel')
        root.dataSelection('grid.sel', 'showcase.movie',
                           columns='$year,$title,$nationality', _fired='^gnr.onStart')
        root.dataRpc('grid.data', 'gridData', _fired='^gnr.onStart')

    def rpc_gridData(self):
        data = Bag()
        data.setItem('r1', None, name='Mark Smith', sex='M', birthday='1980-06-04::D', height=170)
        data.setItem('r2', None, name='Ann Brown', sex='F', birthday='1960-09-21::D', height=173)
        return data

    def gridStruct(self):
        struct = Bag()
        r = struct.child('view').child('rows')
        r.child('cell', field='name', width='20em', name='Name')
        r.child('cell', field='sex', width='2em', name='Sex')
        r.child('cell', field='height', width='3em', name='Height', text_align='right', places=0)
        r.child('cell', field='birthday', width='10em', name='Birthday', format_date='short')
        return struct
        
    
        
