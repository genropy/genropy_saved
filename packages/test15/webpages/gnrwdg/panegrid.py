# -*- coding: UTF-8 -*-

# panegrid.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/palette_manager:PaletteManager"

    def windowTitle(self):
        return ''
        
    def test_0_panegrid(self,pane):
        """Pane grid """
        pane = pane.framePane(height='200px')
        pane.contentPane(height='30px',side='top',background='blue')
        pane.contentPane(margin='10px',background='red')
        
         
    def _test_0_panegrid(self,pane):
        """Pane grid """
        bc = pane.borderContainer(height='200px')
        bc.contentPane(region='left',width='200px',background_color='red')
        paneGrid = bc.paneGrid('province_1',struct='regione',table='glbl.provincia',region='center')
        paneGrid.slotToolbar('province',slots='*,piero',piero='*A,T,D',side='top')
        paneGrid.selectionStore(storepath='.grid.store',table='glbl.provincia',
                                where="$regione='LOM'",gridId='province_1_grid',_onStart=True)   
    
    @struct_method('province_piero')
    def province_piero(self,pane,piero=None,wdgNodeId=None,**kwargs):
        return pane.div(width='205px').searchBox(nodeId='%s_searchbox' %wdgNodeId,searchOn=piero,datapath='.searchbox')
        
    def _test_1_palettegrid(self,pane):
        paneGrid = pane.paletteGrid('province_2',title='Province',
                                    struct='regione',dockTo='*',
                                    table='glbl.provincia',searchOn='*A,T,D')
        paneGrid.selectionStore(storepath='.grid.store',table='glbl.provincia',
                                where="$regione='LOM'",gridId='province_2_grid') 