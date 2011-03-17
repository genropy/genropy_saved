# -*- coding: UTF-8 -*-

# includedview_externalchanges.py
# Created by Francesco Porcari on 2011-03-15.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_iv_standard(self,pane):
        "standard"
        pane = pane.framePane(frameCode='loc_stat',height='200px')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('min')
        view.selectionStore(table='glbl.localita',where="$provincia='AN'",_onStart=True,
                            order_by='$nome',externalChanges=True)
                            
    def test_1_iv_virtual(self,pane):
        "virtual"
        pane = pane.framePane(frameCode='loc_virt',height='200px')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('min')
        view.selectionStore(table='glbl.localita',where="$provincia='AN'",_onStart=True,
                            order_by='$nome',externalChanges=True,chunkSize=10)