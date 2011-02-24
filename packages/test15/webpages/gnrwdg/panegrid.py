# -*- coding: UTF-8 -*-

# framegrid.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
"Test page description"
class GnrCustomWebPage(object):
    testOnly='_zzz_'
    user_polling = 0
    auto_polling = 0
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
    
    def test_0_frame_includedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('regione')
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True,storeCode='mystore')
        
    def test_10_frame_includedview_relationStore(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('regione')
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True,storeCode='mystore')
        
    def test_zzz_frame_includedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='fatture',height='200px')
        tbar = pane.top.slotToolbar('datestart,*,searchOn')
        tbar.datestart.dateTextbox(value='^.date_start')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('min')
        view.selectionStore(table='polimed.fattura',where="$data>:date_start",selectionName='*',chunkSize=30,
                            date_start='^.date_start')
        
    def regione_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome',width='40%')
        r.fieldcell('regione',width='20%')
        r.fieldcell('@regione.nome',width='40%')

        
    def _test_1_frame_includedview_struct(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(struct=self.regione_struct)
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        
    def test_1_frame_includedview_zz(self,pane):
        """Pane XX """
        pane = pane.framePane(frameCode='province',height='200px',datapath='piero')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView()
        view.selectionStore(storepath='guido',table='glbl.provincia',where="$regione='LOM'",_onStart=True)
    
    def test_2_frame_includedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        pane.selectionStore(storeCode='provinceMie',table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(store='provinceMie')
        struct = view.gridStruct('regione')
        

    def test_3_palettegrid(self,pane):
        paletteGrid = pane.paletteGrid(paletteCode='province_2',title='Province',
                                    struct='regione',dockTo='*')
        paletteGrid.selectionStore(table='glbl.provincia',where="$regione=:reg",reg='^.regione') 
        footer = paletteGrid.bottom.slotToolbar('prova,*')
        paletteGrid.top.slotToolbar('searchOn')
        footer.prova.dbSelect(dbtable='glbl.regione',value='^.regione')
        
    
    def test_5_frame_includedview_virtual(self,pane):
        """virtual grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,inputsearch')
        tbar.inputsearch.textbox(value='^.chunk')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('min')
        view.selectionStore(table='glbl.localita',where="$nome ILIKE :chunk",chunk='=="%"+_chunk+"%"',
                            _chunk='^.chunk',virtualSelection=True)
    

   