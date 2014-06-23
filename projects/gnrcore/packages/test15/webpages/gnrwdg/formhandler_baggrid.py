# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    dojo_source = True
    css_requires='public'
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler"""
    
    def test_0_bc(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='600px',datapath='.bh')

        top = bc.contentPane(region='top',height='300px',datapath='.view')
        top.data('.dati',self.getDati())

        top.dataController('SET gridstore = dati.deepCopy();',dati='=.dati',_fired='^zzz',_onStart=True)
        frame = top.bagGrid(frameCode='test_view0',title='Test',struct=self.gridstruct,height='300px',
                            table='glbl.localita',storepath='gridstore')
        frame.bottom.button('Load',fire='zzz')
        center = bc.contentPane(region='center')

        myform = frame.grid.linkedForm(frameCode='test_form0',
                                 datapath='.form',loadEvent='onSelected',
                                 childname='form',formRoot=center,store='memory',store_pkeyField='id')


        center = myform.center.contentPane(datapath='.record')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.provincia',lbl='Provincia',dbtable='glbl.provincia')

        fb.numbertextbox(value='^.qty',lbl='Quantitativo')
        fb.numbertextbox(value='^.colli',lbl='Colli',validate_notnull=True,validate_notnull_error='!!Required')
        myform.top.slotToolbar('*,delete,add,save,semaphore')
#
    def test_1_dialog(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='600px',datapath='.bh')

        top = bc.contentPane(region='center',datapath='.view')
        top.data('.dati',self.getDati())

        top.dataController('SET gridstore = dati.deepCopy();',dati='=.dati',_fired='^zzz',_onStart=True)
        frame = top.bagGrid(frameCode='test_view1',title='Test',struct=self.gridstruct,height='300px',gridEditor=False,
                            table='glbl.localita',storepath='gridstore1',pbl_classes=True,grid_selfDragRows=True)
                            
        myform = frame.grid.linkedForm(frameCode='test_form1',
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='300px',dialog_width='300px',
                                 childname='form',attachTo=top,store='memory',store_pkeyField='id')


        center = myform.center.contentPane(datapath='.record')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.provincia',lbl='Provincia',dbtable='glbl.provincia',selected_nome='.provincia_nome')

        fb.numbertextbox(value='^.qty',lbl='Quantitativo')
        fb.numbertextbox(value='^.colli',lbl='Colli',validate_notnull=True,validate_notnull_error='!!Required')
        myform.top.slotToolbar('navigation,*,delete,add,save,semaphore')

        

    def gridstruct(self, struct):
        r = struct.view().rows()
        r.fieldcell('provincia',table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='L',name='Quantitativo',width='5em')  
        r.cell('colli',dtype='L',name='Colli',width='5em')  
        r.cell('cist',name='Codice istat')

    def getDati(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(provincia = 'MI',qty=13,colli=3,provincia_nome='Milano',cist='044')))
        result.setItem('r_1',Bag(dict(provincia = 'CO',qty=22,colli=1,provincia_nome='Como',cist='039')))
        return result



