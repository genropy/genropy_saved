# -*- coding: UTF-8 -*-

# includedview_externalchanges.py
# Created by Francesco Porcari on 2011-03-15.
# Copyright (c) 2011 Softwell. All rights reserved.

"includedview: externalchanges"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='public'
    
    def windowTitle(self):
        return 'includedview: externalchanges'
         
    def isDeveloper(self):
        return True

    def mystruct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome',width='20em')
        r.fieldcell('provincia',width='10em')
        r.fieldcell('codice_istat',width='7em') 
        r.fieldcell('codice_comune',width='7em')
        r.fieldcell('prefisso_tel',width='4em')
        r.fieldcell('cap',width='7em')
        r.checkboxcolumn(checkedId='.checked_localita')

    def test_0_iv_standard(self,pane):
        "standard"
        pane = pane.framePane(frameCode='loc_stat',height='250px')
        view = pane.includedView(_newGrid=True,struct=self.mystruct)
        view.selectionStore(table='glbl.localita',where="$provincia='AN'",
                            _onStart=True,order_by='$nome',
                            externalChanges=True)


                
    def test_1_iv_virtual(self,pane):
        "virtual"
        pane = pane.framePane(frameCode='loc_virt',height='250px')
        view = pane.includedView(_newGrid=True,struct=self.mystruct)
        view.selectionStore(table='glbl.localita',#where="$provincia='AN'",
                            _onStart=True,order_by='$nome',
                            externalChanges=True,chunkSize=10)
                            