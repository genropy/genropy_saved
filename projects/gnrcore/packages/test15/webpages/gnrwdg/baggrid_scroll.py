# -*- coding: utf-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    dojo_source = True
    css_requires='public'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid,th/th:TableHandler"
    
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^.loadBag')
        pane.dataFormula('.gridstore',"new gnr.GnrBag();",_onStart=True)
        frame = pane.bagGrid(frameCode='test',title='Test',
                                struct=self.gridstruct,
                                height='300px',
                                storepath='.gridstore')
        frame.bottom.button('Load',fire='.loadBag')
        

    def gridstruct(self,struct):
        view_0 = struct.view(fixedColumn=1)
        rows = view_0.rows()
        rows.cell('nome',width='10em',name='Nome')
        #view_1 = struct.view()
        #rows = view_0.rows()
        for i in range(10):
            cs = rows.columnset('cs_{}'.format(i),name='Cs {}'.format(i))
            for j in range(3):
                cs.cell('val_{i:02}{j:02}'.format(i=i,j=j),name='Col {}'.format(i))


    def getDati(self):
        result = Bag()
        for i in range(5):
            row = Bag()
            result.addItem('r_{i:02}'.format(i=i),row)
            row['nome'] = 'row {i:02}'.format(i=i)
            for j in range(10):
                for z in range(3):
                    row['val_{i:02}{j:02}'.format(i=j,j=z)] = i*100+j
        return result