# -*- coding: UTF-8 -*-

# panegrid.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

"panegrid"

class GnrCustomWebPage(object):
    testOnly='_target_action'
    user_polling = 0
    auto_polling = 0
    py_requires="gnrcomponents/testhandler:TestHandlerFull,foundation/includedview"
    
    def test_0_frame_includedview_newgrid(self,pane):
        """Pane grid with export to excel/numbers file"""
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,export')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('regione')
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",
                            _onStart=True,storeCode='mystore0')
                            
    def test_1_frame_includedview_export(self,pane):
        """Pane grid"""
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('searchOn,*,iv_export')
        view = pane.includedView(nodeId='grid_province',_newGrid=True)
        struct = view.gridStruct('regione')
        pane.dataController("alert('export')",subscribe_province_export=True)
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",
                            _onStart=True,storeCode='mystore1')
                            
    def test_2_frame_includedview_virtualIncludedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='fatture',height='200px')
        tbar = pane.top.slotToolbar('datestart,*,searchOn')
        tbar.datestart.dateTextbox(value='^.date_start')
        view = pane.includedView(_newGrid=True) #'.grid
        struct = view.gridStruct('min')
        view.selectionStore(table='polimed.fattura',where="$data>:date_start",
                            selectionName='*',chunkSize=30,date_start='^.date_start')
                            
    def _test_3_frame_includedview_virtualPaletteGrid(self,pane):
        """Pane grid """
        box = pane.div(height='30px')
        palette = box.paletteGrid('fatture_p',struct='min',_newGrid=True,dockTo='*')
        tbar = palette.top.slotToolbar('datestart,*,xxx')
        tbar.datestart.dateTextbox(value='^.date_start')
        tbar.xxx.textbox(value='^.pp',default_value='ppp')
        palette.selectionStore(table='polimed.fattura',where="$data>:date_start",selectionName='*',chunkSize=30,
                               date_start='^.date_start',_if='date_start')
                               
    def regione_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome',width='40%')
        r.fieldcell('regione',width='20%')
        r.fieldcell('@regione.nome',width='40%')
        
    def test_4_frame_includedview_struct(self,pane):
        """searchOn"""
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(struct=self.regione_struct)
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        
    def test_5_frame_includedview_zz(self,pane):
        """searchOn"""
        pane = pane.framePane(frameCode='province',height='200px',datapath='piero')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView()
        view.selectionStore(storepath='guido',table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        
    def test_6_frame_includedview(self,pane):
        """Pane grid"""
        pane = pane.framePane(frameCode='province',height='200px')
        pane.selectionStore(storeCode='provinceMie',table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(store='provinceMie')
        struct = view.gridStruct('regione')
        
    def test_7_frame_includedview_target_action(self,pane):
        """addrow"""
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,addrow')
        view = pane.includedView(selfsubscribe_addrow='console.log("receiving add");')
        struct = view.gridStruct('regione')
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True,storeCode='mystore7')
        
    def test_8_palettegrid(self,pane):
        pane = pane.contentPane(height='50px')
        paletteGrid = pane.paletteGrid(paletteCode='province_2',title='Province d\'Italia',
                                       struct='regione',dockTo='*')
        paletteGrid.top.slotToolbar('searchOn')
        paletteGrid.selectionStore(table='glbl.provincia',where="$regione=:reg",reg='^.nome_regione')
        footer = paletteGrid.bottom.slotToolbar('prova,*')
        footer.prova.dbSelect(dbtable='glbl.regione',value='^.nome_regione')
        
    def test_9_frame_includedview_virtual(self,pane):
        """virtual grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,inputsearch')
        tbar.inputsearch.textbox(value='^.chunk')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('min')
        view.selectionStore(table='glbl.localita',where="$nome ILIKE :chunk",chunk='=="%"+_chunk+"%"',
                            _chunk='^.chunk',virtualSelection=True)
                            
    def _test_10_frame_includedview_framegrid(self,pane):
        pass
        
    #def test_11_frame_includedview_relationStore(self,pane):
    #    """Pane grid """
    #    pane = pane.framePane(frameCode='province',height='200px')
    #    tbar = pane.top.slotToolbar('*,searchOn')
    #    view = pane.includedView(_newGrid=True)
    #    struct = view.gridStruct('regione')
    #    view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True,storeCode='mystore')
    