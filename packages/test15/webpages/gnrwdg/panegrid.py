# -*- coding: UTF-8 -*-

# framegrid.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/palette_manager:PaletteManager"

    def windowTitle(self):
        return ''
    
    def _test_0_frame_includedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView()
        struct = view.gridStruct('regione')
        view.selectionStore(table='glbl.provincia',where="$regione='LOM'",_onStart=True)
    
    def test_1_frame_includedview(self,pane):
        """Pane grid """
        pane = pane.framePane(frameCode='province',height='200px')
        pane.selectionStore(storeCode='provinceMie',table='glbl.provincia',where="$regione='LOM'",_onStart=True)
        tbar = pane.top.slotToolbar('*,searchOn')
        view = pane.includedView(store='provinceMie')
        struct = view.gridStruct('regione')
        

    def test_1_palettegrid(self,pane):
        paletteGrid = pane.paletteGrid(paletteCode='province_2',title='Province',
                                    struct='regione',dockTo='*',searchOn='*A,T,D')
        paletteGrid.selectionStore(table='glbl.provincia',where="$regione='LOM'") 