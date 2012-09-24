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
        r.cell('myset_a',userSets=True,name='A')
        r.cell('myset_b',userSets=True,name='B')



    def test_0_iv_standard(self,pane):
        "standard checkboxcolumn"
        pane = pane.framePane(frameCode='loc_stat',height='250px')
        view = pane.includedView(_newGrid=True,struct=self.mystruct)
        view.selectionStore(table='glbl.localita',where="$provincia='AN'",
                            _onStart=True,order_by='$nome',
                            externalChanges=True)

    def test_2_iv_virtual(self,pane):
        "virtual checkboxcolumn"
        pane = pane.framePane(frameCode='loc_virt',height='250px')
        bar = pane.top.slotToolbar('only_a,only_b,allrows,union')
        bar.only_a.button('Only A',action='SET .grid.currentfilter = objectKeys(myset_a);',myset_a='=.grid.sets.myset_a')
        bar.only_b.button('Only B',action='SET .grid.currentfilter = objectKeys(myset_b);',myset_b='=.grid.sets.myset_b')
        bar.allrows.button('All',action='SET .grid.currentfilter = null;')
        bar.union.button('Union',action='SET .grid.currentfilter = objectKeys(objectUpdate(myset_a,myset_b));',myset_a='=.grid.sets.myset_a',myset_b='=.grid.sets.myset_b')
        view = pane.includedView(_newGrid=True,struct=self.mystruct,userSets='.sets')
        view.selectionStore(table='glbl.localita',where="""^.where""",
                            _onStart=True,order_by='$nome',currentfilter='=.grid.currentfilter',
                            externalChanges=True,chunkSize=10)
        pane.dataController("""
                             SET .where = currentfilter? filtered:allcondition;""",currentfilter='^.grid.currentfilter',
                            filtered="$id IN :currentfilter",allcondition='$id IS NOT NULL')


        pane.bottom.button('Test',action="""SET .grid.sets.myset_b = keys;""",keys='GTpUSNsVEdyZNgAX8t4orw,F6FSbNsVEdyZNgAX8t4orw,F5iWNtsVEdyZNgAX8t4orw')



                            