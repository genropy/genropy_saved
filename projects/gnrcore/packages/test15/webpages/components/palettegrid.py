# -*- coding: utf-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""palette_manager"""

from gnr.core.gnrbag import Bag

"Palettes"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull" #gnrcomponents/palette_manager"
    auto_polling = 0
    user_polling = 0
    
    def windowTitle(self):
        return 'Palette manager'

        
    def test_1_remoteTableHandlerTest(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='top').button('Create',fire='.create')
        center = bc.contentPane(region='center')
        bc.dataController("""
             pane._('ContentPane',{remote:'th_remoteTableHandler',remote_thkwargs:{table:'glbl.provincia'}});
            """,_fired='^.create',pane=center)

    def test_1_paletteGridRemote(self, pane):
        frame = pane.framePane(frameCode='test2',height='400px')
        bar = frame.top.slotToolbar('*,palettetest,5')
        bar.palettetest.paletteGrid(paletteCode='paletteprovincia',table='glbl.provincia',viewResource='View',dockButton=True)


    def test_2_remoteTableForm(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='top').button('Create',fire='.create')
        center = bc.contentPane(region='center')
        bc.dataController("""
             pane._('ContentPane',{remote:'th_remoteTableHandler',
                                    remote_thkwargs:{table:'glbl.provincia',thwidget:'form'}});
            """,_fired='^.create',pane=center)

        