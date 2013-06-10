# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    dojo_source = True
    css_requires='public'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .xxx = dati.deepCopy();',dati='=.dati',_fired='^zzz')
        frame = pane.bagGrid(frameCode='test',title='Test',struct=self.gridstruct,height='300px',
                            table='glbl.localita',storepath='.xxx',default_provincia='MI',default_qty=4)
        frame.bottom.button('Load',fire='zzz')
        #editor = frame.grid.gridEditor()
        #editor.dbSelect(gridcell='provincia',dbtable='glbl.provincia') #zzvalue='^.provincia_sigla'
        
    def gridstruct(self, struct):
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='L',name='Quantitativo',width='5em',edit=True)  
        r.cell('colli',dtype='L',name='Colli',width='5em',edit=True)  
        r.cell('totale',dtype='L',name='Colli',width='5em',formula='colli*qty')  
        r.cell('cist',name='Codice istat')




    def test_1_remotestruct(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .xxx = dati.deepCopy();',dati='=.dati',_fired='^zzz')
        frame = pane.bagGrid(frameCode='test',title='Test',structpath='yyy',height='300px',
                            table='glbl.localita',storepath='.xxx',default_provincia='MI',default_qty=4)
        frame.bottom.button('Load',fire='zzz')

        frame.bottom.button('Load Struct',fire='kkk')
        pane.dataRpc('yyy',self.r_gridstruct,_fired='^kkk')

        #editor = frame.grid.gridEditor()
        #editor.dbSelect(gridcell='provincia',dbtable='glbl.provincia') #zzvalue='^.provincia_sigla'
    
    @public_method
    def r_gridstruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='L',name='Quantitativo',width='5em',edit=True)  
        r.cell('colli',dtype='L',name='Colli',width='5em',edit=True)  
        r.cell('totale',dtype='L',name='Colli',width='5em',formula='colli*qty')  
        r.cell('cist',name='Codice istat')
        return struct

    def getDati(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(provincia = 'MI',qty=13,provincia_nome='Milano',cist='044')))
        result.setItem('r_1',Bag(dict(provincia = 'CO',qty=22,provincia_nome='Como',cist='039')))
        return result
