# -*- coding: UTF-8 -*-

# panegrid.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/palette_manager:PaletteManager"

    def windowTitle(self):
        return ''
         
    def test_0_panegrid(self,pane):
        """Pane grid """
        bc = pane.borderContainer(height='200px')
        bc.contentPane(region='left',width='200px',background_color='red')
        gridPane = bc.paneGrid('province',struct='regione',table='glbl.provincia',region='center',searchOn=True)
        gridPane.selectionStore(storepath='.grid.store',table='glbl.provincia',
                                where="$regione='LOM'",gridId='province_grid',_onStart=True)   
    
    def test_1_palettegrid(self,pane):
        gridPane = pane.paletteGrid('province',title='Province',
                                    struct='regione',dockTo='*',
                                    table='glbl.provincia',searchOn='*A,T,D')
        gridPane.selectionStore(storepath='.grid.store',table='glbl.provincia',
                                where="$regione='LOM'",gridId='palette_province_grid') 